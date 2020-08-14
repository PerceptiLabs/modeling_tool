import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_generator_output_content(script_factory):
    layer_spec = DataEnvironmentSpec(
        id_='layer_id',
        name='layer_name',
        environment_name='Breakout-v0'
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    
    generator = layer.make_generator()
    generator.send(None)
    
    state_info = layer.take_action(generator, layer.action_space[0])
    assert set(state_info.keys()) == set(['output', 'reward', 'done', 'info'])

