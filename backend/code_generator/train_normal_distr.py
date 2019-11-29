from pprint import pprint


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
# ----

BATCH_SIZE_PER_REPLICA = 10
GLOBAL_BATCH_SIZE = BATCH_SIZE_PER_REPLICA * n_devices



strategy = tf.distribute.MirroredStrategy(devices=[f'/CPU:{i}' for i in range(n_devices)])







train_dataset = tf.data.Dataset.zip((datasets[input_data_layer][0], datasets[target_data_layer][0]))

train_iterator = tf.data.Iterator.from_structure(train_dataset.output_types, train_dataset.output_shapes)
train_iterator_init = train_iterator.make_initializer(train_dataset)





validation_dataset = tf.data.Dataset.zip((datasets[input_data_layer][1], datasets[target_data_layer][1]))
test_dataset = tf.data.Dataset.zip((datasets[input_data_layer][2], datasets[target_data_layer][2]))
train_dataset = train_dataset.batch(GLOBAL_BATCH_SIZE)
validation_dataset = validation_dataset.batch(GLOBAL_BATCH_SIZE)
test_dataset = test_dataset.batch(1)







train_iterator = strategy.make_dataset_iterator(train_dataset)
validation_iterator = strategy.make_dataset_iterator(validation_dataset)
#test_iterator = strategy.make_dataset_iterator(test_dataset) # batch size == 1 means no distribution.

def create_model():

    class Model:
        def __init__(self):
            self._locals = {}
        
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

        grads_dict = {}
        for var in tf.trainable_variables():
            name = 'grad-' + var.name
            grads_ = tf.gradients(loss_value, [var])
            assert len(grads_) == 1
            grads_dict[name] = grads_[0]


        
        locals_ = model._locals.copy()

        #for layer_id, layer_locals in locals_.items():
        #    for k, v in list(layer_locals.items()):
        #        if isinstance(v, tf.Tensor):
        #            layer_locals[k] = tf.identity(v)
        #        x=12



        print("train step")        
        #import pdb; pdb.set_trace()

        with tf.control_dependencies([update_vars]):
            return (tf.identity(loss_value), grads_dict, locals_)

    def validation_step(inputs):
        x, y = inputs
        y_pred, y_target = model(x, y)

        loss_value = tf.reduce_sum(tf.square(y_pred - y_target)) / GLOBAL_BATCH_SIZE

        trainable_vars = tf.trainable_variables()
        grads = tf.gradients(loss_value, trainable_vars)        

        grads_dict = {}
        for var in tf.trainable_variables():
            name = 'grad-' + var.name
            grads_ = tf.gradients(loss_value, [var])
            assert len(grads_) == 1
            grads_dict[name] = grads_[0]
            
        return (tf.identity(loss_value), grads_dict, model._locals)



    if n_devices > 1:
        dist_loss, dist_grads_train, dist_locals_train = strategy.experimental_run(train_step, train_iterator)


        #import pdb;pdb.set_trace()
        
        dist_loss = [dist_loss.get(device) for device in dist_loss.devices]
        loss_train = tf.reduce_sum(dist_loss) / n_devices

        for variable, per_replica_obj in dist_grads_train.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]

            assert len(tensors) == 1
            dist_grads_train[variable] = tensors[0]


        dist_loss_validation, dist_grads_val, dist_locals_val = strategy.experimental_run(validation_step, validation_iterator)
        
        dist_loss_validation = dist_loss_validation.values
        loss_validation = tf.reduce_sum(dist_loss_validation) / n_devices

        dist_grads_val = {k: v for k, v in dist_grads_val.items() if v is not None}

        for variable, per_replica_obj in dist_grads_val.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]

            assert len(tensors) == 1
            dist_grads_val[variable] = tensors[0]

    else:
        #dist_loss, dist_grads_train, dist_locals = strategy.experimental_run(train_step, train_iterator)
        #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.

        pass

        
    sess.run(tf.global_variables_initializer())

    all_tensors = api.data.get_tensors()
    pprint(all_tensors)
    print("ALL_tensors")



    from boltons.iterutils import remap
    from collections.abc import Iterable
    def visit(p, k, v):
        if isinstance(v, list) or isinstance(v, dict):
            return len(v) > 0
        else:
            print('aa', p, k, type(v), tf.is_tensor(v))        
            return tf.is_tensor(v)
        
    
    all_tensors = remap(dist_locals_train, visit=visit)

    #import pdb; pdb.set_trace()

        
    
    #import pdb;pdb.set_trace()
    api.data.store(all_tensors=all_tensors)
    api.data.store(max_epoch={{n_epochs - 1}},
                   train_datasize=_data_size[0],
                   val_datasize=_data_size[1])
    
    accuracy = tf.constant(0)
    f1 = tf.constant(0)
    auc = tf.constant(0)

    for epoch in range({{n_epochs}}):
        print(f"epoch{epoch}")
        
        api.data.store(iter_training=0, iter_validation=0)
        api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[], 
                       acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])

        sess.run(train_iterator_init)

    
        
        train_iter=0
        try:
            print("ENTER TRAIN LOOP!")
            
            while True:
                if api.ui.headless:
                    acc_train, loss_train_value, f1_train, auc_train = sess.run([accuracy, loss_train, f1, auc])
                else:
                    acc_train, loss_train_value, f1_train, auc_train, gradient_vals, all_evaled_tensors = sess.run([accuracy, loss_train, f1, auc, dist_grads_train, all_tensors])
                    api.data.store(all_evaled_tensors=all_evaled_tensors)


                    
                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)


                    
                    #pprint(all_evaled_tensors)
                    #print("ZAASA")
                    #import pdb; pdb.set_trace()
                    
                    

                #print("bisrsia")
                #import pdb; pdb.set_trace()
                    
                api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train_value, f1_train_iter=f1_train, auc_train_iter=auc_train)
                api.data.store(iter_training=train_iter)
                
                api.ui.render(dashboard='train_val')

                train_iter+=1
                print("TRAIN ITER", train_iter)
        except tf.errors.OutOfRangeError:
            print("out of range...")

        # TEMPORARY
        continue
        
        sess.run(validation_iterator_init)        
        val_iter=0
        try:
            while True:

                if api.ui.skip:
                    api.ui.skip=False
                    break
                
                if api.ui.headless:
                    acc_val, loss_val, f1_val, auc_val = sess.run([accuracy, loss_validation, f1, auc])
                else:
                    acc_val, loss_validation_value, f1_val, auc_val, gradient_vals, all_evaled_tensors = sess.run([accuracy, loss_validation, f1, auc, dist_grads_val, all_tensors])
                    api.data.store(all_evaled_tensors=all_evaled_tensors) 

                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)

                api.data.stack(acc_val_iter=acc_val, loss_val_iter=loss_validation_value, f1_val_iter=f1_val, auc_val_iter=auc_val)
                api.data.store(iter_validation=val_iter)
                api.ui.render(dashboard='train_val')
                val_iter+=1
                print("VAL ITER", val_iter)                
        except tf.errors.OutOfRangeError:
            print("OUT OF RANGE!")
            pass


        print("BLAAZ")
        
        api.data.store(epoch=epoch)
        api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train_value, f1_training_epoch=f1_train, auc_training_epoch=auc_train,
                       acc_validation_epoch=acc_val, loss_validation_epoch=loss_validation_value, f1_validation_epoch=f1_val, auc_validation_epoch=auc_val)

            
    #import pdb; pdb.set_trace()
    
    print("DONE")
            
            


    
