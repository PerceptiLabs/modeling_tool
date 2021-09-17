import pytest
import numpy as np
from perceptilabs.layers.deeplearningconv.stats import ConvPreviewStats


def test_conv_preview_content():
    sample = np.random.random((224,224,11))
    preview_content = ConvPreviewStats().get_preview_content(sample)
    assert preview_content[1] == (224, 224,11)
    assert preview_content[2] == 551936
    assert not preview_content[3]