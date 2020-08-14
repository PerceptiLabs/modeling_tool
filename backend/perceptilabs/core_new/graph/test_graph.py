import pytest
from unittest.mock import MagicMock, PropertyMock

from perceptilabs.core_new.graph.base import Graph


def test_execution_order_ok_for_branching_graph():
    ''' 
    n1 -> n2 ->
              v
    n3 -> n4 -> n5
    '''
    n1 = MagicMock()
    type(n1).is_training_node = PropertyMock(return_value=False)
    
    n2 = MagicMock()
    type(n2).is_training_node = PropertyMock(return_value=False)

    n3 = MagicMock()
    type(n3).is_training_node = PropertyMock(return_value=False)

    n4 = MagicMock()
    type(n4).is_training_node = PropertyMock(return_value=False)

    n5 = MagicMock()
    type(n5).is_training_node = PropertyMock(return_value=True)

    nodes = [n1, n2, n3, n4, n5]
    edges = [(n1, n2), (n2, n5), (n3, n4), (n4, n5)]    
    g = Graph(nodes, edges)

    order = list(g.nodes)
    assert set([n1, n2, n3, n4, n5]) == set(order)
    assert (
        order.index(n1) < order.index(n2) and
        order.index(n3) < order.index(n4) and
        order.index(n4) < order.index(n5) and
        order.index(n2) < order.index(n5)
    )


def test_execution_order_ok_for_cyclical_graph_with_inner_training_layer():
    ''' 
    n1 -> n2 ->
        v     v
    n3 -> n4 -> n5
    '''
    n1 = MagicMock()
    type(n1).is_training_node = PropertyMock(return_value=False)
    
    n2 = MagicMock()
    type(n2).is_training_node = PropertyMock(return_value=False)

    n3 = MagicMock()
    type(n3).is_training_node = PropertyMock(return_value=False)

    n4 = MagicMock()
    type(n4).is_training_node = PropertyMock(return_value=True)

    n5 = MagicMock()
    type(n5).is_training_node = PropertyMock(return_value=True)

    nodes = [n1, n2, n3, n4, n5]
    edges = [(n1, n2), (n2, n5), (n3, n4), (n4, n5), (n1, n4)]    
    g = Graph(nodes, edges)

    order = list(g.nodes)
    assert set([n1, n2, n3, n4, n5]) == set(order)
    assert (
        order.index(n1) < order.index(n2) and
        order.index(n3) < order.index(n4) and
        order.index(n4) < order.index(n5) and
        order.index(n2) < order.index(n5) and
        order.index(n1) < order.index(n4)
    )


def test_execution_order_ok_for_cyclical_graph():
    ''' 
    n1 -> n2 ->
        v     v
    n3 -> n4 -> n5
    '''
    n1 = MagicMock()
    type(n1).is_training_node = PropertyMock(return_value=False)
    
    n2 = MagicMock()
    type(n2).is_training_node = PropertyMock(return_value=False)

    n3 = MagicMock()
    type(n3).is_training_node = PropertyMock(return_value=False)

    n4 = MagicMock()
    type(n4).is_training_node = PropertyMock(return_value=False)

    n5 = MagicMock()
    type(n5).is_training_node = PropertyMock(return_value=True)

    nodes = [n1, n2, n3, n4, n5]
    edges = [(n1, n2), (n2, n5), (n3, n4), (n4, n5), (n1, n4)]    
    g = Graph(nodes, edges)

    order = list(g.nodes)
    assert set([n1, n2, n3, n4, n5]) == set(order)
    assert (
        order.index(n1) < order.index(n2) and
        order.index(n3) < order.index(n4) and
        order.index(n4) < order.index(n5) and
        order.index(n2) < order.index(n5) and
        order.index(n1) < order.index(n4)
    )
    
    
