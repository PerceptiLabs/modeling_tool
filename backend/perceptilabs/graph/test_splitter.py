import pytest
from perceptilabs.graph.splitter import GraphSplitter


@pytest.fixture
def splitter():
    yield GraphSplitter()

    
def test_single_node_unchanged(splitter):
    node_ids = ['123']
    edges_by_id = []

    results = splitter.split(node_ids, edges_by_id)
    assert results == [(node_ids, edges_by_id)]


def test_two_nodes_give_two_subgraphs(splitter):
    node_ids = ['123', '456']
    edges_by_id = []

    results = splitter.split(node_ids, edges_by_id)
    assert len(results) == 2

    
def test_split_on_single_node_unchanged(splitter):
    node_ids = ['123']
    edges_by_id = []

    results = splitter.split(node_ids, edges_by_id, split_ids=['123'])
    assert results == [(node_ids, edges_by_id)]

    
def test_split_on_last_node_unchanged(splitter):
    node_ids = ['123', '456']
    edges_by_id = [('123', '456')]

    results = splitter.split(node_ids, edges_by_id, split_ids=['456'])
    assert results == [(node_ids, edges_by_id)]
    

def test_split_on_first_node_unchanged(splitter):
    node_ids = ['123', '456']
    edges_by_id = [('123', '456')]

    results = splitter.split(node_ids, edges_by_id, split_ids=['123'])
    assert results == [(node_ids, edges_by_id)]

    
def test_split_on_middle_node_gives_two_graphs(splitter):
    node_ids = ['123', '456', '789']
    edges_by_id = [('123', '456'), ('456', '789')]

    results = splitter.split(node_ids, edges_by_id, split_ids=['456'])

    split1 = (['123', '456'], [('123', '456')])
    split2 = (['456', '789'], [('456', '789')])    
    assert results == [split1, split2] or results == [split2, split1]

    
