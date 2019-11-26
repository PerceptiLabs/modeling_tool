from pprint import pprint


datasets = X['datasets']
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
#test_iterator = strategy.make_dataset_iterator(test_dataset) # this can probably be ran on single gpu

def create_model():

    def model(x, y):
        layer_outputs = {
            input_data_layer: x,
            target_data_layer: y
        }        
        
        for lc in layer_calls:
            layer_id, func, input_layers = lc['layer_id'], lc['func'], lc['input_layers']

            if len(input_layers) == 1:
                X = {'Y': layer_outputs[input_layers[0]]}
            elif len(input_layers) > 1:
                X = {input_id: {'Y': layer_outputs[input_id]} for input_id in input_layers}
            else:
                X = {}
            
            Y = func(layer_id, X)            
            layer_outputs[layer_id] = Y

        return layer_outputs[output_layer], layer_outputs[target_layer]
    
    return model




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

        with tf.control_dependencies([update_vars]):
            return (tf.identity(loss_value), grads_dict)

    def validation_step(inputs):
        x, y = inputs
        y_pred, y_target = model(x, y)

        loss_value_ = tf.reduce_sum(tf.square(y_pred - y_target)) / GLOBAL_BATCH_SIZE

        return tf.identity(loss_value_)


    if n_devices > 1:
        dist_loss, dist_grads_dict = strategy.experimental_run(train_step, train_iterator)

        # Replace all per_replica objects with a dict of tensors instead.
        
        dist_loss = [dist_loss.get(device) for device in dist_loss.devices]
        loss_train = tf.reduce_sum(dist_loss) / n_devices

        for variable, per_replica_obj in dist_grads_dict.items():
            tensors = [per_replica_obj.get(device) for device in per_replica_obj.devices \
                       if per_replica_obj.get(device) is not None]

            assert len(tensors) == 1
            dist_grads_dict[variable] = tensors[0]


        dist_loss_validation = strategy.experimental_run(validation_step, validation_iterator)
        dist_loss_validation = [dist_loss_validation.get(device) for device in dist_loss_validation.devices]
        loss_validation = tf.reduce_sum(dist_loss_validation) / n_devices
    else:
        dist_loss, dist_grads_dict = strategy.experimental_run(train_step, train_iterator)
        #dist_test = strategy.experimental_run(test_step, test_iterator) # TODO: implement this.



        
    sess.run(tf.global_variables_initializer())



    all_tensors = api.data.get_tensors()
    all_tensors = {} # TODO: all tensors messes with the iterators!!! 
    
    api.data.store(all_tensors=all_tensors)
    api.data.store(max_epoch={{n_epochs - 1}},
                   train_datasize=_data_size[0],
                   val_datasize=_data_size[1])
    
    accuracy = tf.constant(0)
    f1 = tf.constant(0)
    auc = tf.constant(0)

    for epoch in range({{n_epochs}}):
        print(f"epoch{epoch}")
        sess.run(train_iterator_init)
        import pdb;pdb.set_trace()

        itr=0
        try:
            while True:
                loss_train_value = sess.run(loss_train)
                itr += 1
                print("itr",itr)
        except:
            print("Except!")
            pass
            

        continue

        
        #api.data.store(iter_training=0, iter_validation=0)
        #api.data.store(acc_train_iter=[], loss_train_iter=[], f1_train_iter=[], auc_train_iter=[], 
        #               acc_val_iter=[], loss_val_iter=[], f1_val_iter=[], auc_val_iter=[])


        train_iter=0
        try:
            print("ENTER TRAIN LOOP!")

            
            while True:
                loss_train = sess.run(loss)
                '''
                if api.ui.headless:
                    acc_train, loss_train, f1_train, auc_train = sess.run([accuracy, loss, f1, auc])
                else:
                    acc_train, loss_train, f1_train, auc_train, gradient_vals, all_evaled_tensors = sess.run([accuracy, loss, f1, auc, dist_grads_dict, all_tensors])
                    api.data.store(all_evaled_tensors=all_evaled_tensors)
        
                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)
        
                api.data.stack(acc_train_iter=acc_train, loss_train_iter=loss_train, f1_train_iter=f1_train, auc_train_iter=auc_train)
                api.data.store(iter_training=train_iter)
                
                api.ui.render(dashboard='train_val')
                '''
                
                train_iter+=1
                print("TRAIN ITER", train_iter)
        except tf.errors.OutOfRangeError:
            print("out of range...")
            
        continue

        sess.run(validation_iterator.initialize())

        #for i in range(10):
        #    loss_val = sess.run(loss_validation)
        #    print(loss_val)

        import pdb;pdb.set_trace()
        
        print("START VALIDATION!")
        val_iter=0
        try:
            while True:

                if api.ui.skip:
                    api.ui.skip=False
                    break
                
                if api.ui.headless:
                    acc_val, loss_val, f1_val, auc_val = sess.run([accuracy, loss_validation, f1, auc])
                else:
                    #acc_val, loss_val, f1_val, auc_val, gradient_vals, all_evaled_tensors = sess.run([accuracy, loss_validation, f1, auc, dist_grads_dict, all_tensors])
                    loss_val = sess.run(loss_validation)                    
                    api.data.store(all_evaled_tensors=all_evaled_tensors) 

                    new_gradient_vals={}
                    for gradName, gradValue in gradient_vals.items():
                         new_gradient_vals[gradName+':Min'] = np.min(np.min(gradValue))
                         new_gradient_vals[gradName+':Max'] = np.max(np.max(gradValue))
                         new_gradient_vals[gradName+':Average'] = np.average(gradValue)
                    api.data.stack(**new_gradient_vals)

                    
                #api.data.stack(acc_val_iter=acc_val, loss_val_iter=loss_val, f1_val_iter=f1_val, auc_val_iter=auc_val)
                api.data.store(iter_validation=val_iter)
                api.ui.render(dashboard='train_val')
                val_iter+=1
                print("VAL ITER", val_iter)                
        except tf.errors.OutOfRangeError:
            print("OUT OF RANGE!")
            pass


        print("BLAAZ")
        
        #api.data.store(epoch=epoch)
        #api.data.stack(acc_training_epoch=acc_train, loss_training_epoch=loss_train, f1_training_epoch=f1_train, auc_training_epoch=auc_train,
        #               acc_validation_epoch=acc_val, loss_validation_epoch=loss_val, f1_validation_epoch=f1_val, auc_validation_epoch=auc_val)

            
    #import pdb; pdb.set_trace()
    
    print("DONE")
            
            


    
