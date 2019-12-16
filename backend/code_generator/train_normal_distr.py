from pprint import pprint

INCLUDE_KERAS_METRICS = True

self_layer_name = layer_name # this is passed as input
datasets = {layer_id: wrapper(layer_id, None) for layer_id, wrapper in X['datasets'].items()} # Datasets are created immediately. Files don't HAVE TO be read here, but the type of iterators are dictated by the training layer and should therefore be created here.
layer_calls = X['layer_calls'] # Mapping of inputs between layers and 'layer wrappers'. Essentially a copy of 'json network'

input_data_layer = '{{input_data_layer}}' # used to (1) distinguish inputs and labels, (2) attach data tensors to locals of data dict and. These are only available after train_step has run
target_data_layer = '{{target_data_layer}}'
output_layer = '{{output_layer}}' # used to (1) define the outputs of the wrapped model, (2) define the inputs dict, 'X', of the training layer (both for train, val and test)
target_layer = '{{target_layer}}'

# ---- temporary: the enclosed part is only for simulating more than one device.
n_devices = 2
config = tf.ConfigProto(device_count={"CPU": n_devices},
                        inter_op_parallelism_threads=n_devices,
                        intra_op_parallelism_threads=1,
                        log_device_placement=True)

# ----
sess = tf.Session(config=config)
tf.keras.backend.set_session(sess) # since we use keras metrics


BATCH_SIZE_PER_REPLICA = 10 # TODO: get from frontend/json network
GLOBAL_BATCH_SIZE = BATCH_SIZE_PER_REPLICA * n_devices

strategy = tf.distribute.MirroredStrategy(devices=[f'/CPU:{i}' for i in range(n_devices)]) # TODO: not needed under real circumstances, should default to all.

train_dataset = tf.data.Dataset.zip((datasets[input_data_layer][0], datasets[target_data_layer][0]))
validation_dataset = tf.data.Dataset.zip((datasets[input_data_layer][1], datasets[target_data_layer][1]))
test_dataset = tf.data.Dataset.zip((datasets[input_data_layer][2], datasets[target_data_layer][2]))

train_dataset = train_dataset.batch(GLOBAL_BATCH_SIZE)
validation_dataset = validation_dataset.batch(GLOBAL_BATCH_SIZE)
test_dataset = test_dataset.batch(1) # Since the batch size for test is 1, it does not make sense to divide the batch over several replicas. Do testing as usual.

# NOTE: A key difference for distributed: we have one _iterator_ per dataset, as opposed to one _initializer_ per dataset in the normal case.
# This means that we have to create a different version of all metrics (accuracy, f1, auc, etc), the gradients and more importantly: 'all tensors'.

train_iterator = strategy.make_dataset_iterator(train_dataset)
validation_iterator = strategy.make_dataset_iterator(validation_dataset)

test_iterator = tf.data.Iterator.from_structure(test_dataset.output_types, test_dataset.output_shapes)
test_iterator_init = test_iterator.make_initializer(test_dataset)

def create_model():
    # The tensors generated by distributed iterators are only accessible locally from each replica. Therefore,
    # each replica must create its own version of the model. This has the following two consequences:
    #
    #     * all tensorflow variables/operations must be executed on device, once per replica => the wrapped layers are further wrapped as a Model.
    #     * we must keep track of the created variables, so that the validation steps can reuse the trained variables => we use get_variable instead of tf.Variable, with a var-scope for each layer.
    #     * we will have several instances/copies of non-trainable/non-tensorflow variables. => Each layer wrapper tracks the number of times it's been created, or they would overwrite eachother.
    
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

    if INCLUDE_KERAS_METRICS:
        # contrib.f1_score and metrics.auc do not work with distributed. 
        # note: f1_score seems to be deprecated in tf2.0, so it makes sense that they haven't imported it in tf 2.0
        # https://stackoverflow.com/questions/53620581/calculate-f1-score-using-tf-metrics-precision-recall-in-a-tf-estimator-setup
        #
        # Likewise, AUC does not work properly for distributed. Keras metrics seem to be the recommended approach.
        # This works out of the box for AUC, but not for F1 score (not implemented). Using definition and going via Recall and Precision instead.
        
        num_thresholds=200
        epsilon = 1e-7
        thresholds = [(i+0) * 1.0 / (num_thresholds - 1) for i in range(num_thresholds - 0)]
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
        locals_[input_data_layer] = {'Y': x} # output/preview. hack hack hack [see beginning of script for explanation]
        locals_[target_data_layer] = {'Y': y} # this layer is not run here.....:/

        locals_[self_layer_name] = {'X': {
            output_layer: {'Y': y_target}, # inputs to this layer...
            target_layer: {'Y': y_pred}
        }}


        correct_predictions = tf.equal(tf.argmax(y_pred,-1), tf.argmax(y_target,-1))
        accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))


        print("train step")        

        with tf.control_dependencies(update_ops):
            return (tf.identity(loss_value), accuracy, grads_dict, locals_)

    def validation_step(inputs):
        x, y = inputs
        y_pred, y_target = model(x, y)

        loss_value = tf.reduce_sum(tf.square(y_pred - y_target)) / GLOBAL_BATCH_SIZE

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
            
        with tf.control_dependencies(update_ops):            
            return (tf.identity(loss_value), accuracy, grads_dict, locals_)

    if n_devices > 1:
        dist_loss, acc_train_, dist_grads_train, dist_locals_train = strategy.experimental_run(train_step, train_iterator)

        dist_loss = [dist_loss.get(device) for device in dist_loss.devices]
        loss_train = tf.reduce_sum(dist_loss)

        acc_train_ = tf.reduce_mean(acc_train_.values) # TODO: how to aggregate?
        
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
        dist_grads_val = {k: v for k, v in dist_grads_val.items() if v is not None}

        for variable, per_replica_obj in dist_grads_val.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]
            dist_grads_val[variable] = tensors[0]

    else:
        #dist_loss, dist_grads_train, dist_locals = strategy.experimental_run(train_step, train_iterator)
        #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.
        pass

    sess.run(tf.global_variables_initializer())
    
    if INCLUDE_KERAS_METRICS:
        sess.run([v.initializer for v in auc_train.variables])  # these need spec. treatment when initializing
        sess.run([v.initializer for v in recall_train.variables])
        sess.run([v.initializer for v in precision_train.variables])
        sess.run([v.initializer for v in auc_val.variables]) 
        sess.run([v.initializer for v in recall_val.variables])
        sess.run([v.initializer for v in precision_val.variables])

    from boltons.iterutils import remap
    from collections.abc import Iterable

    def get_tensors(dist_locals):
        all_tensors = dist_locals
        
        # CONVERT PERREPLICAS TO _FIRST_ TENSOR. PERHAPS SOME FORM OF AGGREGATION IS NEEDED.
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

    api.data.store(all_tensors=all_tensors)
    api.data.store(max_epoch={{n_epochs - 1}},
                   train_datasize=_data_size[0],
                   val_datasize=_data_size[1])
    
    if not INCLUDE_KERAS_METRICS:
        auc_train_tensor = tf.constant(-1)
        auc_val_tensor = tf.constant(-2)
        f1_train = tf.constant(-3)
        f1_val = tf.constant(-4)        

    for epoch in range({{n_epochs}}):
        print(f"entering epoch {epoch}")
        
        api.data.store(iter_training=0, iter_validation=0)
        api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[], 
                       acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])

        sess.run(train_iterator_init)
        
        train_iter = 0
        try:
            while True:
                if api.ui.headless:
                    acc_train, loss_train_value = sess.run([acc_train_, loss_train])
                else:
                    acc_train, loss_train_value, gradient_vals, all_evaled_tensors = sess.run([acc_train_, loss_train, dist_grads_train, all_tensors])
                    api.data.store(all_evaled_tensors=all_evaled_tensors)
                    
                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)

                auc_train_val = sess.run(auc_train_tensor)
                f1_train_val = sess.run(f1_train)                

                api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train_value, f1_train_iter=f1_train_val, auc_train_iter=auc_train_val)
                api.data.store(iter_training=train_iter)
                
                api.ui.render(dashboard='train_val')

                if INCLUDE_KERAS_METRICS:
                    auc_train.reset_states()
                    recall_train.reset_states()
                    precision_train.reset_states()                                
                
                train_iter += 1
        except tf.errors.OutOfRangeError:
            print("out of range [training]...")

        sess.run(validation_iterator_init)

        val_iter=0
        try:
            while True:
                if api.ui.skip:
                    api.ui.skip = False
                    break
                
                if api.ui.headless:
                    acc_val, loss_validation_value = sess.run([acc_val_, loss_validation])
                else:
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
            print("out of range [validation]...")

        api.data.store(epoch=epoch)
        api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train_value, f1_training_epoch=f1_train_val, auc_training_epoch=auc_train_val,
                       acc_validation_epoch=acc_val, loss_validation_epoch=loss_validation_value, f1_validation_epoch=f1_val_val, auc_validation_epoch=auc_val_val)

        
    api.data.store(max_iter_testing=_data_size[2])
    sess.run(test_iterator_init)
    iter = 0
    x, y = test_iterator.get_next()    
    y_pred, y_target = model(x, y)

    # all tensors test
    model._locals = {}
    locals_ = model._locals.copy()
    locals_[input_data_layer] = {'Y': x} # output/preview. hack hack hack
    locals_[target_data_layer] = {'Y': y} # this layer is not run here.....:/
    
    locals_[self_layer_name] = {'X': {
        output_layer: {'Y': y_target}, # inputs to this layer...
        target_layer: {'Y': y_pred}
    }}
    
    all_tensors_test = get_tensors(locals_)
    try:
        while True:
            all_evaled_tensors = sess.run(all_tensors_test)
            api.data.store(all_tensors=all_evaled_tensors)
            api.data.store(iter_testing=iter)
            iter+=1
            api.ui.render(dashboard='testing')  
    except tf.errors.OutOfRangeError:      
        pass
