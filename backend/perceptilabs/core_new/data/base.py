import copy


class DataContainer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._data_dict = dict()        

    def _create_subdict_if_needed(self, layer_id):
        if not layer_id in self._data_dict:
            self._data_dict[layer_id] = dict()

    def store_value_in_root(self, name, value):
        self._data_dict[name] = value

    def store_value(self, layer_id, name, value):
        self._create_subdict_if_needed(layer_id)
        self._data_dict[layer_id][name] = value

    def stack_value(self, layer_id, name, value):
        self._create_subdict_if_needed(layer_id)

        try:
            self._data_dict[layer_id][name].append(value)
            if len(self._data_dict[layer_id][name])>500:
                self._data_dict[layer_id][name].pop(0)
        except AttributeError:
            print("warning, overwriting existing value!")
            self._data_dict[layer_id][name] = [value]
        except KeyError:
            self._data_dict[layer_id][name] = [value]

    def evaluate_dict(self, d):
        import tensorflow as tf
        if type(d) is dict:
            new_d={}
            for key, value in d.items():
                new_d[key] = self.evaluate_dict(value)
                if new_d[key] is None or new_d[key]=={}:
                    new_d.pop(key)
            return new_d

        if tf.contrib.framework.is_tensor(d):
            return d

    def on_tensors_get(self):
        return self.evaluate_dict(self.to_dict())

    def __getitem__(self, id_):
        data = copy.copy(self._data_dict.get(id_))
        return data

    def __contains__(self, id_):
        return id_ in self._data_dict

    def to_dict(self):
        data_dict = copy.copy(self._data_dict)
        return data_dict

    
