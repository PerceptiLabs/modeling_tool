import pytest
import numpy as np
from perceptilabs.layers.unet.stats import UnetPreviewStats


def test_unet_preview_content():
    sample = np.random.randint(0,2,(224,224,11))
    preview_content = UnetPreviewStats().get_preview_content(sample)
    assert preview_content[0] == [sample]
    assert preview_content[1] == (224, 224,11)
    assert preview_content[2] == 551936
    assert preview_content[3] == ['mask']