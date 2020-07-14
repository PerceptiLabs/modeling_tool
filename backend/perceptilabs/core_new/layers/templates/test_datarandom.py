import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import skimage
import pkg_resources


from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT



@pytest.fixture(scope='module')
def j2_engine():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory)
    yield j2_engine


def test_make_generator_sequence_unaffected_by_numpy_seed_call(j2_engine):

    layer = create_layer(
        j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        'DataRandom',
        shape = (1),
        distribution = 'Normal',
        mean = 0.0,
        stddev = 1.0,
        minval = 0,
        maxval = 0,
        seed_training = 3890,
        seed_testing = 5678,
        seed_validation = 1234
    )

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
