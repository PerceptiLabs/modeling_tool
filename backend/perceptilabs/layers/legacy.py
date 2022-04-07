import tensorflow as tf


class Tf2xLayer:
    """This layer is an adapter between Keras layers and our infrastructure for sending data.

    NOTE: The properties of this layer likely have to be updated as new TF2 layers are added. For example, make sure all weights are returned with the correct name.
    """

    def __init__(self, keras_class):
        self._keras_class = keras_class
        self._keras_layer = None
        self._outputs = {"output": None}

    @property
    def keras_layer(self):
        if self._keras_layer is None:
            self._keras_layer = self._keras_class()
        return self._keras_layer

    def __call__(self, *args, **kwargs):
        self._outputs = self.keras_layer(*args, **kwargs)
        return self._outputs

    def get_sample(self):
        vars_ = self._outputs.copy()
        if "preview" in vars_:
            vars_["output"] = vars_[
                "preview"
            ]  # Overwrite the output with the preview variable.
        else:
            raise RuntimeError(
                "Could not fetch 'preview' variable from Keras layer. "
                "This variable must be declared as an output in order for "
                "the previews to work properly."
            )
        return vars_

    @property
    def variables(self):
        return self.keras_layer.get_config()

    @property
    def trainable_variables(self):
        dict_ = {}
        dict_.update(self.weights)
        dict_.update(self.biases)
        return dict_

    @property
    def weights(self):
        """Return the trainable weight of a layer"""
        if hasattr(self.keras_layer, "kernel") and hasattr(
            self.keras_layer.kernel, "trainable"
        ):
            if self.keras_layer.kernel.trainable:
                return {"W": self.keras_layer.kernel}
        elif (
            hasattr(self.keras_layer, "conv")
            and hasattr(self.keras_layer.conv, "kernel")
            and hasattr(self.keras_layer.conv.kernel, "trainable")
        ):
            if self.keras_layer.conv.kernel.trainable:
                return {"W": self.keras_layer.conv.kernel}
        else:
            return {}

    @property
    def biases(self):
        """Return the trainable bias of a layer"""
        if hasattr(self.keras_layer, "bias") and hasattr(
            self.keras_layer.bias, "trainable"
        ):
            if self.keras_layer.bias.trainable:
                return {"b": self.keras_layer.bias}
        elif (
            hasattr(self.keras_layer, "conv")
            and hasattr(self.keras_layer.conv, "bias")
            and hasattr(self.keras_layer.conv.bias, "trainable")
        ):
            if self.keras_layer.conv.kernel.trainable:
                return {"b": self.keras_layer.conv.bias}
        else:
            return {}


class DataSupervised:
    pass


class Picklable:
    pass


import pickle


def can_serialize(object_):
    try:
        pickle.dumps(object_)
    except:
        return False
    else:
        return True


def serialize(object_):
    return pickle.dumps(object_)
