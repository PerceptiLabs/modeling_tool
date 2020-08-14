import pytest

import numpy as np
import tensorflow as tf


from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.datarandom.spec import DataRandomSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_shape_is_ok(script_factory):
    expected_shape = (12, 34, 56)
    
    layer_spec = DataRandomSpec(
        id_='layer_id',
        name='layer_name',
        shape=expected_shape
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    generator = layer.make_generator_training()
    actual_shape = next(generator)['output'].shape

    assert actual_shape == expected_shape

def test_make_generator_sequence_unaffected_by_numpy_seed_call(script_factory):

    layer_spec = DataRandomSpec(
        id_='layer_id',
        name='layer_name',
        shape=(1),
        distribution='Normal',
        mean=0.0,
        stddev=1.0,
        minval=0,
        maxval=10,
        seed_training=3890,
        seed_testing=5678,
        seed_validation=1234
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
        
    training_generator_1 = layer.make_generator_training()
    training_samples = [next(training_generator_1) for _ in range(10)]
    training_generator_2 = layer.make_generator_training()
    training_samples_new = [next(training_generator_2) for _ in range(5)]

    validation_generator_1 = layer.make_generator_training()
    validation_samples = [next(validation_generator_1) for _ in range(10)]
    validation_generator_2 = layer.make_generator_training()
    validation_samples_new = [next(validation_generator_2) for _ in range(5)]

    testing_generator_1 = layer.make_generator_training()
    testing_samples = [next(testing_generator_1) for _ in range(10)]
    testing_generator_2 = layer.make_generator_training()
    testing_samples_new = [next(testing_generator_2) for _ in range(5)]

    np.random.seed(2324)

    for _ in range(5):
        training_samples_new.append(next(training_generator_2))
        validation_samples_new.append(next(validation_generator_2))
        testing_samples_new.append(next(testing_generator_2))

    assert training_samples == training_samples_new
    assert testing_samples == testing_samples_new
    assert validation_samples == validation_samples_new
