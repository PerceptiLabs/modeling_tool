import dill
import pytest
from unittest.mock import MagicMock, PropertyMock

from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import ReplicatedProperty
from perceptilabs.core_new.serialization import can_serialize

@pytest.mark.integtest
def test_graph_is_rebuilt_from_snapshot():
    class MyLayer:
        @property
        def accuracy(self):
            return 0.123

    class MyReplica:
        def __init__(self, accuracy):
            self._accuracy = accuracy

        @property
        def accuracy(self):
            return self._accuracy
    
    base_to_replica_map = {MyLayer: MyReplica}
    replica_by_name = {MyReplica.__name__: MyReplica}
    replicated_properties_table = {MyLayer: [ReplicatedProperty('accuracy', float, -1)]}
    
    gb = GraphBuilder()
    sb = SnapshotBuilder(base_to_replica_map, replicated_properties_table, fn_can_serialize=can_serialize)
    gb_replica = GraphBuilder(replica_by_name)    
    
    graph = gb.build_from_layers_and_edges(
        layer_map={'123': MyLayer()},
        edges_by_id={}
    )

    snapshot = sb.build(graph)
    graph_replica = gb_replica.build_from_snapshot(snapshot)

    assert graph.nodes[0].layer_id == graph_replica.nodes[0].layer_id
    assert graph.nodes[0].layer.accuracy == graph_replica.nodes[0].layer.accuracy














