import pytest

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.layercustom.spec import LayerCustomSpec


@pytest.fixture(scope="module")
def script_factory():
    yield ScriptFactory()


@pytest.mark.skip  # TODO(anton.k): remove marker in story 1779
def test_default_returns_inputs(script_factory):
    layer_spec = LayerCustomSpec(id_="layer_id", name="layer_name")
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    inputs = {"input": "some-value"}
    outputs = layer(inputs)

    assert outputs["output"] == inputs["input"]


def test_returns_exact_code(script_factory):
    expected_code = 'print("Hello!!!!")'

    layer_spec = LayerCustomSpec(
        id_="layer_id", name="layer_name", custom_code=expected_code
    )

    actual_code = LayerHelper(script_factory, layer_spec).get_code()
    assert actual_code == expected_code
