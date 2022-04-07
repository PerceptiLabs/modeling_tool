import pytest

from perceptilabs.graph.spec import GraphSpec


def test_from_dict_raises_error_on_non_dict():
    not_a_dictionary = 123
    with pytest.raises(ValueError):
        GraphSpec.from_dict(not_a_dictionary)


def test_from_dict_raises_error_on_non_dict_layers():
    not_a_dictionary = 123
    graph_spec_dict = {"123": not_a_dictionary}

    with pytest.raises(ValueError):
        GraphSpec.from_dict(graph_spec_dict)
