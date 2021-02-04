from collections import namedtuple
from perceptilabs.layers.datadata.spec import DataDataSpec
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec
from perceptilabs.layers.datarandom.spec import DataRandomSpec
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.deeplearningconv.spec import DeepLearningConvSpec
from perceptilabs.layers.deeplearningdeconv.spec import DeepLearningDeconvSpec
from perceptilabs.layers.deeplearningrecurrent.spec import DeepLearningRecurrentSpec
from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.processrescale.spec import ProcessRescaleSpec
from perceptilabs.layers.processgrayscale.spec import ProcessGrayscaleSpec
from perceptilabs.layers.mathargmax.spec import MathArgmaxSpec
from perceptilabs.layers.mathsoftmax.spec import MathSoftmaxSpec
from perceptilabs.layers.mathswitch.spec import MathSwitchSpec
from perceptilabs.layers.mathmerge.spec import MathMergeSpec
from perceptilabs.layers.layercustom.spec import LayerCustomSpec
from perceptilabs.layers.trainclassification.spec import TrainClassificationSpec
from perceptilabs.layers.trainregression.spec import TrainRegressionSpec
from perceptilabs.layers.trainreinforce.spec import TrainReinforceSpec
from perceptilabs.layers.trainobjectdetection.spec import TrainObjectDetectionSpec
from perceptilabs.layers.traingan.spec import TrainGanSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec

LayerMeta = namedtuple(
    'LayerMeta', [
        'spec_class',
        'imports_path',
        'macro_path',        
        'macro_name',
    ]
)

DEFINITION_TABLE = {
    'DataData': LayerMeta(
        DataDataSpec,
        'layers/datadata/imports.json',
        'core_new/layers/templates/datadata.j2',        
        'layer_datadata'
    ),
    'DataEnvironment': LayerMeta(
        DataEnvironmentSpec,
        'layers/dataenvironment/imports.json',
        'core_new/layers/templates/dataenv.j2',        
        'layer_dataenvironment'
    ),
    'DataRandom': LayerMeta(
        DataRandomSpec,
        'layers/datarandom/imports.json',
        'core_new/layers/templates/datarandom.j2',        
        'layer_datarandom'
    ),
    'DeepLearningFC': LayerMeta(
        DeepLearningFcSpec,
        'layers/deeplearningfc/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_fully_connected'
    ),
    'DeepLearningConv': LayerMeta(
        DeepLearningConvSpec,
        'layers/deeplearningconv/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_conv'
    ),
    'DeepLearningDeconv': LayerMeta(
        DeepLearningDeconvSpec,
        'layers/deeplearningdeconv/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_deconv'
    ),
    'DeepLearningRecurrent': LayerMeta(
        DeepLearningRecurrentSpec,
        'layers/deeplearningrecurrent/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_recurrent'
    ),
    'ProcessOneHot': LayerMeta(
        ProcessOneHotSpec,
        'layers/processonehot/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_one_hot'
    ),
    'ProcessReshape': LayerMeta(
        ProcessReshapeSpec,
        'layers/processreshape/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_reshape'
    ),
    'ProcessRescale': LayerMeta(
        ProcessRescaleSpec,
        'layers/processrescale/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_image_reshape'
    ),
    'ProcessGrayscale': LayerMeta(
        ProcessGrayscaleSpec,
        'layers/processreshape/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_grayscale'
    ),
    'MathArgmax': LayerMeta(
        MathArgmaxSpec,
        'layers/mathargmax/imports.json',
        'layers/mathargmax/template.j2',        
        'layer_tf1x_argmax'
    ),
    'MathSoftmax': LayerMeta(
        MathSoftmaxSpec,
        'layers/mathsoftmax/imports.json',
        'layers/mathsoftmax/template.j2',        
        'layer_tf1x_softmax'
    ),
    'MathSwitch': LayerMeta(
        MathSwitchSpec,
        'layers/mathswitch/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_switch'
    ),
    'MathMerge': LayerMeta(
        MathMergeSpec,
        'layers/mathmerge/imports.json',
        'core_new/layers/templates/tf1x.j2',        
        'layer_tf1x_merge'
    ),
    'LayerCustom': LayerMeta(
        LayerCustomSpec,
        'layers/layercustom/imports.json',
        'core_new/layers/templates/custom.j2',        
        'layer_custom_inner'
    ),
    'TrainNormal': LayerMeta(
        TrainClassificationSpec,
        'layers/trainclassification/imports.json',
        'core_new/layers/templates/tf1x_classification.j2',        
        'layer_tf1x_classification'
    ),
    'TrainRegression': LayerMeta(
        TrainRegressionSpec,
        'layers/trainregression/imports.json',
        'core_new/layers/templates/tf1x_regression.j2',        
        'layer_tf1x_regression'
    ),        
    'TrainReinforce': LayerMeta(
        TrainReinforceSpec,
        'layers/trainreinforce/imports.json',
        'core_new/layers/templates/tf1x_rl.j2',        
        'layer_tf1x_rl'
    ),
    'TrainDetector': LayerMeta(
        TrainObjectDetectionSpec,
        'layers/trainobjectdetection/imports.json',
        'core_new/layers/templates/tf1x_object_detection.j2',        
        'layer_tf1x_object_detection'
    ),
    'TrainGan': LayerMeta(
        TrainGanSpec,
        'layers/traingan/imports.json',
        'core_new/layers/templates/tf1x_gan.j2',        
        'layer_tf1x_gan'
    )        
    
}


DEFINITION_TABLE_TF2X = {
    'DataData': LayerMeta(
        DataDataSpec,
        'layers/datadata/imports.json',
        'core_new/layers/templates/datadata.j2',        
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
        DeepLearningFcSpec,
        'layers/processonehot/tf2x_imports.json',
        'layers/processonehot/tf2x_template.j2',        
        'layer_tf2x_one_hot'
    ),
    'MathSwitch': LayerMeta(
        MathSwitchSpec,
        'layers/mathswitch/tf2x_imports.json',
        'layers/mathswitch/tf2x_template.j2',        
        'layer_tf2x_switch'
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
    'IoInput': LayerMeta(
        InputLayerSpec,
        imports_path=None,
        macro_path=None,
        macro_name=None
    ),
}

