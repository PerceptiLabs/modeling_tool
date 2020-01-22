from abc import ABC, abstractmethod


class Replicator:
    def __init__(self, layer, session_id, layer_id, server):
        self._identifier = f'{session_id}+{layer_id}'
        self._server = server
        self._layer = layer
    
    @abstractmethod
    def synchronize(self):
        raise NotImplementedError

    def _add_assign(self, key, value):
        self._server.add_assign(self._identifier, key, value)

    def _commit(self):
        self._server.commit()
        
    
class DataLayerReplicator(Replicator):
    def synchronize(self):        
        self._add_assign('sample', self._layer.sample)
        self._add_assign('size_training', self._layer.size_training)
        self._add_assign('size_validation', self._layer.size_validation)
        self._add_assign('size_testing', self._layer.size_testing)
        
    
class Tf1xClassificationLayerReplicator(DataLayerReplicator):
    def synchronize(self):
        self._add_assign('sample', self._layer.sample)
        self._add_assign('size_training', self._layer.size_training)
        self._add_assign('size_validation', self._layer.size_validation)
        self._add_assign('size_testing', self._layer.size_testing)
        self._add_assign('accuracy_training', self._layer.accuracy_training)
        self._add_assign('accuracy_validation', self._layer.accuracy_validation)
        self._add_assign('accuracy_testing', self._layer.accuracy_testing)        
        self._add_assign('status', self._layer.status)                        


class Tf1xLayerReplicator(Replicator):
    def synchronize(self):    
        pass
    
