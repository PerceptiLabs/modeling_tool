import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


@pytest.mark.skip(reason="blocks pipeline. gym is very low prio right now, so wont look for root cause")
@pytest.mark.pre_datawizard
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


# NOTE: Testing the unity environment involves loading a unity environment object and running an iteration of it, which opens up the 
# unity env in a separate window. This would in all likelihood cause the build pipeline to fail in any pull request, so for now, skip 
# any unit tests relating to unity.
@pytest.mark.skip
@pytest.mark.pre_datawizard
def test_generator_output_content_unity_basic(script_factory):
    layer_spec = DataEnvironmentSpec(
        id_='layer_id',
        name='layer_name',
        environment_name="Basic",
        timeout_wait=3.0,
        use_unity=True,
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    
    generator = layer.make_generator()
    generator.send(None)
    
    state_info = layer.take_action(generator, layer.action_space[0])
    assert set(state_info.keys()) == set(['output', 'reward', 'done', 'info'])


# Test if we can load the obstacle tower environment. Skip this becuase this test takes a long time.  
@pytest.mark.skip
def test_generator_output_content_unity_obstacletower(script_factory):
    layer_spec = DataEnvironmentSpec(
        id_='layer_id',
        name='layer_name',
        environment_name="ObstacleTower",
        unity_env_path='https://storage.googleapis.com/obstacle-tower-build/v4.1/obstacle_tower_v4.1.yaml', 
        timeout_wait=6.0,
        use_unity=True,
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    
    generator = layer.make_generator()
    generator.send(None)
    
    state_info = layer.take_action(generator, layer.action_space[0])
    assert set(state_info.keys()) == set(['output', 'reward', 'done', 'info'])

