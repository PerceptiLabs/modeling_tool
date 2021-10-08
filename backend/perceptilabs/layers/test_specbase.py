import hashlib
from unittest.mock import MagicMock
from perceptilabs.layers.specbase import DummySpec


def test_hash_value_is_different_for_different_custom_codes():
    obj1 = DummySpec(custom_code='123')
    obj2 = DummySpec(custom_code='321')
    assert obj1.compute_field_hash() != obj2.compute_field_hash()
