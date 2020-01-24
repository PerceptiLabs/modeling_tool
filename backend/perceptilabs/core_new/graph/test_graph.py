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
    
    
def test_split_linear_graph():
    ''' 
    n1 -> n2 -> n3 -> n4 -> n5
    '''

    n1 = MagicMock(name='n1')
    type(n1).is_training_node = PropertyMock(return_value=False)
    
    n2 = MagicMock(name='n2')
    type(n2).is_training_node = PropertyMock(return_value=False)

    n3 = MagicMock(name='n3')
    type(n3).is_training_node = PropertyMock(return_value=True)

    n4 = MagicMock(name='n4')
    type(n4).is_training_node = PropertyMock(return_value=False)

    n5 = MagicMock(name='n5')
    type(n5).is_training_node = PropertyMock(return_value=True)

    nodes = [n1, n2, n3, n4, n5]
    edges = [(n1, n2), (n2, n3), (n3, n4), (n4, n5)]

    g = Graph(nodes, edges)
    assert list(g.nodes) == [n1, n2, n3, n4, n5]
    
    subgraphs = g.trainable_subgraphs
    assert len(subgraphs) == 2

    assert list(subgraphs[0].nodes) == [n1, n2, n3]        
    assert list(subgraphs[1].nodes) == [n1, n2, n3, n4, n5]


def test_split_branching_graph():
    ''' 
    n1 -> n2 -> n3 -> n4 -> n5
            /           /
    n6 -> n7          n8 
    '''

    n1 = MagicMock()
    type(n1).is_training_node = PropertyMock(return_value=False)
    
    n2 = MagicMock()
    type(n2).is_training_node = PropertyMock(return_value=False)

    n3 = MagicMock()
    type(n3).is_training_node = PropertyMock(return_value=True)

    n4 = MagicMock()
    type(n4).is_training_node = PropertyMock(return_value=False)

    n5 = MagicMock()
    type(n5).is_training_node = PropertyMock(return_value=True)

    n6 = MagicMock()
    type(n6).is_training_node = PropertyMock(return_value=False)

    n7 = MagicMock()
    type(n7).is_training_node = PropertyMock(return_value=False)

    n8 = MagicMock()
    type(n8).is_training_node = PropertyMock(return_value=False)
    
    nodes = [n1, n2, n3, n4, n5, n6, n7, n8]
    edges = [(n1, n2), (n2, n3), (n3, n4), (n4, n5), (n6, n7), (n7, n3), (n8, n5)]
    
    g = Graph(nodes, edges)
    
    subgraphs = g.trainable_subgraphs
    assert len(subgraphs) == 2
    
    order = list(subgraphs[0].nodes)
    assert set([n1, n2, n3, n6, n7]) == set(order)
    assert (
        order.index(n1) < order.index(n2) and
        order.index(n2) < order.index(n3) and
        order.index(n6) < order.index(n7) and
        order.index(n7) < order.index(n3)
    )
    
    order = list(subgraphs[1].nodes)
    assert set([n1, n2, n3, n4, n5, n6, n7, n8]) == set(order)    
    assert (
        order.index(n1) < order.index(n2) and
        order.index(n2) < order.index(n3) and
        order.index(n3) < order.index(n4) and
        order.index(n4) < order.index(n5) and
        order.index(n6) < order.index(n7) and
        order.index(n7) < order.index(n3) and
        order.index(n8) < order.index(n5)
    )
    

def test_split_cyclical_graph():
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

    subgraphs = g.trainable_subgraphs
    order = list(subgraphs[0].nodes)

    assert set([n1, n3, n4]) == set(order)
    assert (
        order.index(n1) < order.index(n4) and
        order.index(n3) < order.index(n4) 
    )

    order = list(subgraphs[1].nodes)

    assert set([n1, n2, n3, n4, n5]) == set(order)
    assert (
        order.index(n1) < order.index(n4) and
        order.index(n3) < order.index(n4) and
        order.index(n4) < order.index(n5) and
        order.index(n2) < order.index(n5) 
    )

    
    
    
    



