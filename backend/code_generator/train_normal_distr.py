from pprint import pprint

INCLUDE_KERAS_METRICS = True

self_layer_name = layer_name # this is passed as input
datasets = {layer_id: wrapper(layer_id, None) for layer_id, wrapper in X['datasets'].items()}
layer_calls = X['layer_calls']

input_data_layer = '{{input_data_layer}}'
target_data_layer = '{{target_data_layer}}'
output_layer = '{{output_layer}}'
target_layer = '{{target_layer}}'


# ---- temporary
n_devices = 2
config = tf.ConfigProto(device_count={"CPU": n_devices},
                        inter_op_parallelism_threads=n_devices,
                        intra_op_parallelism_threads=1,
                        log_device_placement=True)

sess = tf.Session(config=config)
tf.keras.backend.set_session(sess) # since we use keras metrics
# ----

BATCH_SIZE_PER_REPLICA = 10
GLOBAL_BATCH_SIZE = BATCH_SIZE_PER_REPLICA * n_devices



strategy = tf.distribute.MirroredStrategy(devices=[f'/CPU:{i}' for i in range(n_devices)])







train_dataset = tf.data.Dataset.zip((datasets[input_data_layer][0], datasets[target_data_layer][0])).take(100) # TODO: REMOVE THESE TAKES
validation_dataset = tf.data.Dataset.zip((datasets[input_data_layer][1], datasets[target_data_layer][1])).take(100) # TODO: REMOVE THESE TAKES
test_dataset = tf.data.Dataset.zip((datasets[input_data_layer][2], datasets[target_data_layer][2]))

train_dataset = train_dataset.batch(GLOBAL_BATCH_SIZE)
validation_dataset = validation_dataset.batch(GLOBAL_BATCH_SIZE)
test_dataset = test_dataset.batch(1)



#train_iterator = tf.data.Iterator.from_structure(train_dataset.output_types, train_dataset.output_shapes)
test_iterator = tf.data.Iterator.from_structure(test_dataset.output_types, test_dataset.output_shapes)
test_iterator_init = test_iterator.make_initializer(test_dataset)



train_iterator = strategy.make_dataset_iterator(train_dataset)
validation_iterator = strategy.make_dataset_iterator(validation_dataset)
#test_iterator = strategy.make_dataset_iterator(test_dataset) # batch size == 1 means no distribution.

def create_model():

    class Model:
        def __init__(self):
            self._locals = {}
            self._wrappers = []
        
        def __call__(self, x, y):
            layer_outputs = {
                input_data_layer: x,
                target_data_layer: y
            }        
        
            for lc in layer_calls:
                layer_id, wrapper, input_layers = lc['layer_id'], lc['wrapper'], lc['input_layers']
                
                if len(input_layers) == 1:
                    X = {'Y': layer_outputs[input_layers[0]]}
                elif len(input_layers) > 1:
                    X = {input_id: {'Y': layer_outputs[input_id]} for input_id in input_layers}
                else:
                    X = {}

                self._wrappers.append(wrapper)
                Y = wrapper(layer_id, X)            
                layer_outputs[layer_id] = Y

                if layer_id not in self._locals:
                    self._locals[layer_id] = wrapper._locals
                else:
                    self._locals[layer_id].update(wrapper._locals)
                    
            return layer_outputs[output_layer], layer_outputs[target_layer]        
    
    return Model()




with strategy.scope():
    train_iterator = strategy.make_dataset_iterator(train_dataset)
    validation_iterator = strategy.make_dataset_iterator(validation_dataset)
    #test_iterator = strategy.make_dataset_iterator(test_dataset) # this can probably be ran on single g


    if INCLUDE_KERAS_METRICS:
        num_thresholds=200
        epsilon = 1e-7
        thresholds = [(i+0) * 1.0 / (num_thresholds - 1)
                      for i in range(num_thresholds - 0)]
        #thresholds = [0.0] + thresholds + [1.0]    
        recall_train = tf.keras.metrics.Recall(thresholds=thresholds)
        precision_train = tf.keras.metrics.Precision(thresholds=thresholds)
        
        r = recall_train.result()
        p = precision_train.result()
        
        f1_train = tf.reduce_max(tf.math.divide_no_nan(2*r*p, r+p)) # TODO: create custom metric instead? make PR at tf?
        auc_train = tf.keras.metrics.AUC(curve='ROC')
        auc_train_tensor = auc_train.result()
        
        recall_val = tf.keras.metrics.Recall(thresholds=thresholds)
        precision_val = tf.keras.metrics.Precision(thresholds=thresholds)
        
        r = recall_val.result()
        p = precision_val.result()
        
        f1_val = tf.reduce_max(tf.math.divide_no_nan(2*r*p, r+p)) # TODO: create custom metric instead? make PR at tf?    
        auc_val = tf.keras.metrics.AUC(curve='ROC')
        auc_val_tensor = auc_val.result()
        
        
    model = create_model()

    train_iterator_init = train_iterator.initialize()
    validation_iterator_init = validation_iterator.initialize()    
    
    
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01*n_devices) # lr proportional to batch size per linear scaling rule



    def train_step(inputs):
        # Each training step runs this custom function which calculates
        # gradients and updates weights.
        x, y = inputs
        y_pred, y_target = model(x, y)

        loss_value = tf.reduce_sum(tf.square(y_pred - y_target)) / GLOBAL_BATCH_SIZE
        #loss_value = tf.nn.compute_average_loss(loss_value, global_batch_size=GLOBAL_BATCH_SIZE)


        trainable_vars = tf.trainable_variables()
        grads = tf.gradients(loss_value, trainable_vars)        
        update_vars = optimizer.apply_gradients(zip(grads, trainable_vars))

        if INCLUDE_KERAS_METRICS:
            update_auc = auc_train.update_state(y_target, y_pred)
            update_recall = recall_train.update_state(y_target, y_pred)
            update_precision = precision_train.update_state(y_target, y_pred)
            
            update_ops = [update_vars, update_auc, update_recall, update_precision]
        else:
            update_ops = [update_vars]
        
        grads_dict = {}
        for var in tf.trainable_variables():
            name = 'grad-' + var.name
            grads_ = tf.gradients(loss_value, [var])
            assert len(grads_) == 1
            grads_dict[name] = grads_[0]

        locals_ = model._locals.copy()
        locals_[input_data_layer] = {'Y': x} # output/preview. hack hack hack
        locals_[target_data_layer] = {'Y': y} # this layer is not run here.....:/

        locals_[self_layer_name] = {'X': {
            output_layer: {'Y': y_target}, # inputs to this layer...
            target_layer: {'Y': y_pred}
        }}


        # TODO: aggregate tp/fp/tn/fn over all replicas and then derive these values for the total? for now, take average.
        #accuracy, acc_op = tf.metrics.accuracy(y_target, y_pred)

        correct_predictions = tf.equal(tf.argmax(y_pred,-1), tf.argmax(y_target,-1))
        accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

        #f1, f1_ops = tf.contrib.metrics.f1_score(y_target, y_pred)
        #f1 = tf.constant(0.123)
        #auc, auc_op = tf.metrics.auc(labels=y_target, predictions=y_pred, curve='ROC')


        print("train step")        
        #import pdb; pdb.set_trace()

        with tf.control_dependencies(update_ops):
            return (tf.identity(loss_value), accuracy, grads_dict, locals_)

    def validation_step(inputs):
        x, y = inputs
        y_pred, y_target = model(x, y)

        loss_value = tf.reduce_sum(tf.square(y_pred - y_target)) / GLOBAL_BATCH_SIZE

        # TODO: aggregate tp/fp/tn/fn over all replicas and then derive these values for the total? for now, take average.
        correct_predictions = tf.equal(tf.argmax(y_pred,-1), tf.argmax(y_target,-1))
        accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))


        if INCLUDE_KERAS_METRICS:
            update_auc = auc_val.update_state(y_target, y_pred)
            update_recall = recall_val.update_state(y_target, y_pred)
            update_precision = precision_val.update_state(y_target, y_pred)
            update_ops = [update_auc, update_recall, update_precision]
        else:
            update_ops = []
                
        
        trainable_vars = tf.trainable_variables()
        grads = tf.gradients(loss_value, trainable_vars)        

        grads_dict = {}
        for var in tf.trainable_variables():
            name = 'grad-' + var.name
            grads_ = tf.gradients(loss_value, [var])
            assert len(grads_) == 1
            grads_dict[name] = grads_[0]

        locals_ = model._locals.copy()
        locals_[input_data_layer] = {'Y': x} # output/preview. hack hack hack
        locals_[target_data_layer] = {'Y': y} # this layer is not run here.....:/

        locals_[self_layer_name] = {'X': {
            output_layer: {'Y': y_target}, # inputs to this layer...
            target_layer: {'Y': y_pred}
        }}
            
        print("validation step")        
        #import pdb; pdb.set_trace()

        with tf.control_dependencies(update_ops):            
            return (tf.identity(loss_value), accuracy, grads_dict, locals_)



    if n_devices > 1:
        dist_loss, acc_train_, dist_grads_train, dist_locals_train = strategy.experimental_run(train_step, train_iterator)


        
        dist_loss = [dist_loss.get(device) for device in dist_loss.devices]
        loss_train = tf.reduce_sum(dist_loss)

        acc_train_ = tf.reduce_mean(acc_train_.values) # TODO: how to aggregate?
        #f1_train_ = tf.reduce_mean(f1_train_.values)
        #auc_train_ = tf.reduce_mean(auc_train_.values)                        


        print("jjjjj")
        #import pdb;pdb.set_trace()

        for variable, per_replica_obj in dist_grads_train.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]

            #assert len(tensors) == 1 
            dist_grads_train[variable] = tensors[0]


        # RESET THESE SO THAT LOCALS BOUND TO FIRST ITERATOR IS OMITTED FOR SECOND INIT.
        for w in model._wrappers:
            w._locals = {}
            w._n_calls = 0
        model._locals = {}

        dist_loss_validation, acc_val_, dist_grads_val, dist_locals_val = strategy.experimental_run(validation_step, validation_iterator)
        dist_loss_validation = dist_loss_validation.values
        loss_validation = tf.reduce_sum(dist_loss_validation)

        acc_val_ = tf.reduce_mean(acc_val_.values)
        #f1_val_ = tf.reduce_mean(f1_val_.values)
        #auc_val_ = tf.reduce_mean(auc_val_.values)                        

        dist_grads_val = {k: v for k, v in dist_grads_val.items() if v is not None}

        for variable, per_replica_obj in dist_grads_val.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]

            #assert len(tensors) == 1
            dist_grads_val[variable] = tensors[0]

    else:
        #dist_loss, dist_grads_train, dist_locals = strategy.experimental_run(train_step, train_iterator)
        #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.

        pass

        
    sess.run(tf.global_variables_initializer())
    
    if INCLUDE_KERAS_METRICS:
        sess.run([v.initializer for v in auc_train.variables])  # these need spec. treatment
        sess.run([v.initializer for v in recall_train.variables])
        sess.run([v.initializer for v in precision_train.variables])
        sess.run([v.initializer for v in auc_val.variables])  # these need spec. treatment
        sess.run([v.initializer for v in recall_val.variables])
        sess.run([v.initializer for v in precision_val.variables])

    #all_tensors = api.data.get_tensors()
    #pprint(all_tensors)
    #print("ALL_tensors")



    from boltons.iterutils import remap
    from collections.abc import Iterable

    #all_tensors = dist_locals_train

    def get_tensors(dist_locals):
        all_tensors = dist_locals
        
        # CONVERT PERREPLICAS TO FIRST TENSOR
        def visit(p, k, v):
            if isinstance(v, tf.python.distribute.values.PerReplica):
                return (k, v.get(v.devices[0]))
            else:
                return (k, v)
        all_tensors = remap(all_tensors, visit=visit)

        # RETAIN TENSORS ONLY!
        def visit(p, k, v):
            if isinstance(v, list) or isinstance(v, dict):
                return len(v) > 0
            else:
                #print('aa', p, k, type(v), tf.is_tensor(v))        
                return tf.is_tensor(v)
        
        all_tensors = remap(all_tensors, visit=visit)
        return all_tensors

    all_tensors = get_tensors(dist_locals_train)
    all_tensors_val = get_tensors(dist_locals_val)

    #import pdb;pdb.set_trace()
    api.data.store(all_tensors=all_tensors)
    api.data.store(max_epoch={{n_epochs - 1}},
                   train_datasize=_data_size[0],
                   val_datasize=_data_size[1])
    
    #acc_train_= tf.constant(0.6)
    #f1_train_ = tf.constant(0.3)
    #auc_train_ = tf.constant(0.3)


    if not INCLUDE_KERAS_METRICS:
        auc_train_tensor = tf.constant(-1)
        auc_val_tensor = tf.constant(-2)
        f1_train = tf.constant(-3)
        f1_val = tf.constant(-4)        

    for epoch in range({{n_epochs}}):
    #for epoch in range(10): # TMP     . use above
        print(f"entering epoch {epoch}")
        
        api.data.store(iter_training=0, iter_validation=0)
        api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[], 
                       acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])

        sess.run(train_iterator_init)

    
        
        train_iter=0
        W_test = None
        try:
            print("ENTER TRAIN LOOP!")
            
            while True:
                if api.ui.headless:
                    acc_train, loss_train_value=sess.run([acc_train_, loss_train])
                else:
                    print("loop")
                    #import pdb; pdb.set_trace()
                    
                    acc_train, loss_train_value, gradient_vals, all_evaled_tensors = sess.run([acc_train_, loss_train, dist_grads_train, all_tensors])
                    api.data.store(all_evaled_tensors=all_evaled_tensors)


                    
                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)

                #import pdb; pdb.set_trace()

                auc_train_val = sess.run(auc_train_tensor)
                f1_train_val = sess.run(f1_train)                

                
                print("auc",auc_train_val)
                print("f1",f1_train_val)                
                #import pdb;pdb.set_trace()
                    
                print("ACC TRAIN", acc_train)

                if W_test is None: # JUST TO VERIFY THAT WEIGHTS _DO_ CHANGE DURING TRAINING
                    W_test = all_evaled_tensors['1564399782856']['W']
                else:
                    assert np.any(W_test != all_evaled_tensors['1564399782856']['W'])
                
                    
                    #pprint(all_evaled_tensors)
                    #print("ZAASA")
                    #import pdb; pdb.set_trace()
                    
                    

                #print("bisrsia")
                #import pdb; pdb.set_trace()
                    
                api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train_value, f1_train_iter=f1_train_val, auc_train_iter=auc_train_val)
                api.data.store(iter_training=train_iter)
                
                api.ui.render(dashboard='train_val')



                if INCLUDE_KERAS_METRICS:
                    auc_train.reset_states()
                    recall_train.reset_states()
                    precision_train.reset_states()                                

                
                train_iter+=1
                print("TRAIN ITER", train_iter)
        except tf.errors.OutOfRangeError:
            print("out of range...")


        # these two are temporary until validation is fixed.
        #api.data.store(epoch=epoch)
        
        #api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train_value, f1_training_epoch=f1_train, auc_training_epoch=auc_train,
        #               acc_validation_epoch=acc_train, loss_validation_epoch=loss_train_value, f1_validation_epoch=f1_train, auc_validation_epoch=auc_train)


        print("JAJAJ")
        #import pdb; pdb.set_trace()
            
        sess.run(validation_iterator_init)

        #print("post initi")
        #import pdb; pdb.set_trace()
        
        val_iter=0

        W_test = None
        
        try:
            while True:

                if api.ui.skip:
                    api.ui.skip=False
                    break
                
                if api.ui.headless:
                    acc_val, loss_validation_value = sess.run([acc_val_, loss_validation])
                else:
                    #pprint(all_tensors_val)
                    #print("all tensors val")
                    #import pdb; pdb.set_trace()
                    print("zz")
                    #import pdb;pdb.set_trace()
                    acc_val, loss_validation_value, gradient_vals, all_evaled_tensors = sess.run([acc_val_, loss_validation, dist_grads_val, all_tensors_val])
                    api.data.store(all_evaled_tensors=all_evaled_tensors) 

                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)


                auc_val_val = sess.run(auc_val_tensor)
                f1_val_val = sess.run(f1_val)
                #f1_val_val = 0.1234
                    

                if W_test is None: # JUST TO VERIFY THAT WEIGHTS _DONT_ CHANGE DURING VALIDATION
                    #print("LOSSES:", loss_train_value, loss_validation_value)                    
                    W_test = all_evaled_tensors['1564399782856']['W']
                else:
                    assert np.all(W_test == all_evaled_tensors['1564399782856']['W'])
                
                api.data.stack(acc_val_iter=acc_val, loss_val_iter=loss_validation_value, f1_val_iter=f1_val_val, auc_val_iter=auc_val_val)
                api.data.store(iter_validation=val_iter)
                api.ui.render(dashboard='train_val')


                if INCLUDE_KERAS_METRICS:
                    auc_val.reset_states()
                    recall_val.reset_states()
                    precision_val.reset_states()                                

                
                val_iter+=1
                print("VAL ITER", val_iter)                
        except tf.errors.OutOfRangeError as e:
            print("OUT OF RANGE! ", repr(e))
            pass


        print("BLAAZ")

        api.data.store(epoch=epoch)
        api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train_value, f1_training_epoch=f1_train_val, auc_training_epoch=auc_train_val,
                       acc_validation_epoch=acc_val, loss_validation_epoch=loss_validation_value, f1_validation_epoch=f1_val_val, auc_validation_epoch=auc_val_val)


    #import pdb; pdb.set_trace()
    

            

    #import pdb; pdb.set_trace()


    
    api.data.store(max_iter_testing=_data_size[2])
    sess.run(test_iterator_init)
    iter = 0
    x, y = test_iterator.get_next()    
    y_pred, y_target = model(x, y)    
    try:
        while True:



            y_pred_val, y_target_val = sess.run([y_pred, y_target])

            #import pdb; pdb.set_trace()
            
            #all_evaled_tensors = sess.run(all_tensors)
            #api.data.store(all_tensors=all_evaled_tensors)
            api.data.store(iter_testing=iter)
            iter+=1
            api.ui.render(dashboard='testing')  
    except tf.errors.OutOfRangeError:      
        pass
