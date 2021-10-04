from collections import namedtuple
from perceptilabs.layers.datadata.spec import DataDataSpec
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec
from perceptilabs.layers.datarandom.spec import DataRandomSpec
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.deeplearningconv.spec import DeepLearningConvSpec
from perceptilabs.layers.deeplearningrecurrent.spec import DeepLearningRecurrentSpec
from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.processrescale.spec import ProcessRescaleSpec
from perceptilabs.layers.processgrayscale.spec import ProcessGrayscaleSpec
from perceptilabs.layers.mathargmax.spec import MathArgmaxSpec
from perceptilabs.layers.mathsoftmax.spec import MathSoftmaxSpec
from perceptilabs.layers.mathmerge.spec import MathMergeSpec
from perceptilabs.layers.layercustom.spec import LayerCustomSpec
from perceptilabs.layers.trainclassification.spec import TrainClassificationSpec
from perceptilabs.layers.trainregression.spec import TrainRegressionSpec
from perceptilabs.layers.trainreinforce.spec import TrainReinforceSpec
from perceptilabs.layers.trainobjectdetection.spec import TrainObjectDetectionSpec
from perceptilabs.layers.traingan.spec import TrainGanSpec
from perceptilabs.layers.pretrainedvgg16.spec import PreTrainedVGG16Spec
from perceptilabs.layers.pretrainedresnet50.spec import PreTrainedResNet50Spec
from perceptilabs.layers.pretrainedinceptionv3.spec import PreTrainedInceptionV3Spec
from perceptilabs.layers.pretrainedmobilenetv2.spec import PreTrainedMobileNetV2Spec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec
from perceptilabs.layers.unet.spec import UNetSpec

LayerMeta = namedtuple(
    'LayerMeta', [
        'spec_class',
        'imports_path',
        'macro_path',
        'macro_name',
    ]
)

DEFINITION_TABLE_TF2X = {
    'DataData': LayerMeta(
        DataDataSpec,
        'layers/datadata/imports.json',
        'layers/datadata/template.j2',
        'layer_datadata'
    ),
    'DeepLearningConv': LayerMeta(
        DeepLearningConvSpec,
        'layers/deeplearningconv/tf2x_imports.json',
        'layers/deeplearningconv/tf2x_template.j2',
        'layer_tf2x_conv'
    ),
    'DeepLearningFC': LayerMeta(
        DeepLearningFcSpec,
        'layers/deeplearningfc/tf2x_imports.json',
        'layers/deeplearningfc/tf2x_template.j2',
        'layer_tf2x_fully_connected'
    ),
    'DeepLearningRecurrent': LayerMeta(
        DeepLearningRecurrentSpec,
        'layers/deeplearningrecurrent/tf2x_imports.json',
        'layers/deeplearningrecurrent/tf2x_template.j2',
        'layer_tf2x_recurrent'
    ),
    'ProcessReshape': LayerMeta(
        ProcessReshapeSpec,
        'layers/processreshape/tf2x_imports.json',
        'layers/processreshape/tf2x_template.j2',
        'layer_tf2x_reshape'
    ),
    'ProcessRescale': LayerMeta(
        ProcessRescaleSpec,
        'layers/processrescale/tf2x_imports.json',
        'layers/processrescale/tf2x_template.j2',
        'layer_tf2x_rescale'
    ),
    'ProcessOneHot': LayerMeta(
        ProcessOneHotSpec,
        'layers/processonehot/tf2x_imports.json',
        'layers/processonehot/tf2x_template.j2',
        'layer_tf2x_one_hot'
    ),
    'ProcessGrayscale': LayerMeta(
        ProcessGrayscaleSpec,
        'layers/processgrayscale/tf2x_imports.json',
        'layers/processgrayscale/tf2x_template.j2',
        'layer_tf2x_grayscale'
    ),
    'MathMerge': LayerMeta(
        MathMergeSpec,
        'layers/mathmerge/tf2x_imports.json',
        'layers/mathmerge/tf2x_template.j2',
        'layer_tf2x_merge'
    ),
    'TrainNormal': LayerMeta(
        TrainClassificationSpec,
        'layers/trainclassification/tf2x_imports.json',
        'layers/trainclassification/tf2x_template.j2',
        'layer_tf2x_classification'
    ),
    'PreTrainedVGG16': LayerMeta(
        PreTrainedVGG16Spec,
        'layers/pretrainedvgg16/tf2x_imports.json',
        'layers/pretrainedvgg16/tf2x_template.j2',
        'layer_pretrained_vgg16'
    ),
    'PreTrainedMobileNetV2': LayerMeta(
        PreTrainedMobileNetV2Spec,
        'layers/pretrainedmobilenetv2/tf2x_imports.json',
        'layers/pretrainedmobilenetv2/tf2x_template.j2',
        'layer_pretrained_mobilenetv2'
    ),
    'PreTrainedResNet50': LayerMeta(
        PreTrainedResNet50Spec,
        'layers/pretrainedresnet50/tf2x_imports.json',
        'layers/pretrainedresnet50/tf2x_template.j2',
        'layer_pretrained_resnet50'
    ),
    'PreTrainedInceptionV3': LayerMeta(
        PreTrainedInceptionV3Spec,
        'layers/pretrainedinceptionv3/tf2x_imports.json',
        'layers/pretrainedinceptionv3/tf2x_template.j2',
        'layer_pretrained_inceptionv3'
    ),
    'UNet': LayerMeta(
        UNetSpec,
        'layers/unet/tf2x_imports.json',
        'layers/unet/tf2x_template.j2',
        'layer_u_net'
    ),
    'IoOutput': LayerMeta(
        OutputLayerSpec,
        imports_path=None,
        macro_path=None,
        macro_name=None
    ),
    'IoInput': LayerMeta(
        InputLayerSpec,
        imports_path=None,
        macro_path=None,
        macro_name=None
    ),
    'LayerCustom': LayerMeta(
        LayerCustomSpec,
        'layers/layercustom/tf2x_imports.json',
        'layers/layercustom/tf2x_template.j2',
        'layer_custom'
    ),
}

