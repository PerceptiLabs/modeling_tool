import tensorflow as tf
from perceptilabs.layers.helper import LayerHelper


class TrainingModel(tf.keras.Model):
    def __init__(self, script_factory, graph_spec):
        super().__init__()

        self._script_factory = script_factory
        self._graph_spec = graph_spec
        
        self._layers_by_id = {}
        for layer_spec in self._graph_spec.get_ordered_layers():
            if layer_spec.is_inner_layer:                    
                self._layers_by_id[layer_spec.id_] = self._get_layer_from_spec(layer_spec)

    @property
    def graph_spec(self):
        return self._graph_spec                   
            
    def call(self, inputs, training=False):
        outputs = {}
        outputs_by_layer = {}
                
        for layer_spec in self._graph_spec.get_ordered_layers():
            if layer_spec.is_input_layer:
                outputs_by_layer[layer_spec.id_] = {'output': inputs[layer_spec.feature_name]}
            elif layer_spec.is_inner_layer:
                layer = self._layers_by_id[layer_spec.id_]
                x = {connection.dst_var: outputs_by_layer[connection.src_id][connection.src_var] for connection in layer_spec.input_connections}
                y = layer(x)

                outputs_by_layer[layer_spec.id_] = y

                for connection in layer_spec.output_connections:
                    output_spec = self._graph_spec[connection.dst_id]
                    if output_spec.is_target_layer:
                        outputs[output_spec.feature_name] = outputs_by_layer[layer_spec.id_]['output']

        return (outputs, outputs_by_layer)

    @property
    def layers_by_id(self):
        return self._layers_by_id.copy()

    def _get_layer_from_spec(self, layer_spec):
        return LayerHelper(self._script_factory, layer_spec, self._graph_spec).get_instance().keras_layer

    def as_inference_model(self, data_loader, include_preprocessing=True):
        if include_preprocessing:
            dataset = data_loader.get_dataset(apply_pipelines='loader') # Model expects data to be loaded but NOT preprocessed
        else:
            dataset = data_loader.get_dataset(apply_pipelines='all')  # Model expects data to be loaded AND preprocessed
            
        inputs_batch, _ = next(iter(dataset))       

        inputs = {}
        for layer_spec in self._graph_spec.input_layers:
            shape = inputs_batch[layer_spec.feature_name].shape
            dtype = inputs_batch[layer_spec.feature_name].dtype

            inputs[layer_spec.feature_name] = tf.keras.Input(
                shape=shape,
                dtype=dtype,
                name=layer_spec.feature_name # Giving the input a name allows us to pass dicts in. https://github.com/tensorflow/tensorflow/issues/34114#issuecomment-588574494
            )

        processed_inputs = inputs.copy()  # Maybe do additional processing before feeding the model

        if include_preprocessing:
            processed_inputs = {
                feature_name: data_loader.get_preprocessing_pipeline(feature_name)(tensor)
                for feature_name, tensor in processed_inputs.items()
            }

        outputs, _ = self.__call__(processed_inputs)

        if include_preprocessing:        
            for feature_name, tensor in outputs.items():
                postprocessing = data_loader.get_postprocessing_pipeline(feature_name)
                outputs[feature_name] = postprocessing(tensor)

        inference_model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return inference_model
        
    
