# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("skimage.io._plugins")

#block_cipher = pyi_crypto.PyiBlockCipher(key='sjdielskaospelsk')

#('/home/vagrant/.local/lib/python3.6/site-packages/tensorflow/contrib/rnn/python/ops/','/tensorflow/contrib/rnn/python/ops/'),('/home/vagrant/.local/lib/python3.6/site-packages/tensorflow/contrib/rnn/python/ops/_gru_ops.so','/tensorflow/contrib/rnn/python/ops/'),('/home/vagrant/.local/lib/python3.6/site-packages/tensorflow/contrib/coder/python/ops/_coder_ops.so','/tensorflow/contrib/coder/python/ops/'),('/home/vagrant/.local/lib/python3.6/site-packages/tensorflow/contrib/bigtable/python/ops/_bigtable.so','/tensorflow/contrib/bigtable/python/ops/'),
import pathlib
import os
from distutils.sysconfig import get_python_lib
from pprint import pformat
from logging import getLogger
log = getLogger(__name__)


working_dir = os.getcwd()

python_lib = get_python_lib()
log.info("python_lib = " + python_lib)


pathex = [working_dir,
          python_lib+'/tensorflow']

binaries = [(python_lib+'/dask/dask.yaml','./dask/'),
            (working_dir+'/appServer.cpython-36m-x86_64-linux-gnu.so', '.'),
            (working_dir+'/s3buckets.cpython-36m-x86_64-linux-gnu.so', '.'),            
            (python_lib+'/tensorflow/contrib/bigtable/python/ops/_bigtable.so', './tensorflow/contrib/bigtable/python/ops'),
            (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
            (python_lib+'/tensorflow/contrib/rnn/python/ops/_gru_ops.so', './tensorflow/contrib/rnn/python/ops/'),
            (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
            (python_lib+'/tensorflow/contrib/tensor_forest/python/ops/_tensor_forest_ops.so', './tensorflow/contrib/tensor_forest/python/ops/'),
            (python_lib+'/tensorflow/contrib/tensor_forest/python/ops/_model_ops.so', './tensorflow/contrib/tensor_forest/python/ops/'),
            (python_lib+'/tensorflow/contrib/tensor_forest/python/ops/_stats_ops.so', './tensorflow/contrib/tensor_forest/python/ops/'),                        
            (python_lib+'/tensorflow/contrib/tensor_forest/libforestprotos.so', './tensorflow/contrib/tensor_forest/'),                                    
            (python_lib+'/tensorflow/contrib/resampler/python/ops/_resampler_ops.so', './tensorflow/contrib/resampler/python/ops'),
            (python_lib+'/tensorflow/contrib/seq2seq/python/ops/_beam_search_ops.so', './tensorflow/contrib/seq2seq/python/ops'),                        
            (python_lib+'/tensorflow/contrib/memory_stats/python/ops/_memory_stats_ops.so', './tensorflow/contrib/memory_stats/python/ops'),
            (python_lib+'/tensorflow/contrib/periodic_resample/python/ops/_periodic_resample_op.so', './tensorflow/contrib/periodic_resample/python/ops'),                        
            (python_lib+'/tensorflow/contrib/image/python/ops/_distort_image_ops.so', './tensorflow/contrib/image/python/ops'),
            (python_lib+'/tensorflow/contrib/image/python/ops/_image_ops.so', './tensorflow/contrib/image/python/ops'),
            (python_lib+'/tensorflow/contrib/image/python/ops/_single_image_random_dot_stereograms.so', './tensorflow/contrib/image/python/ops'),                                    
            (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),
            (python_lib+'/tensorflow/contrib/factorization/python/ops/_clustering_ops.so', './tensorflow/contrib/factorization/python/ops'),
            (python_lib+'/tensorflow/contrib/factorization/python/ops/_factorization_ops.so', './tensorflow/contrib/factorization/python/ops'),            
            (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),                       
            (python_lib+'/tensorflow/contrib/rnn/python/ops/_lstm_ops.so', './tensorflow/contrib/rnn/python/ops/'),
            (python_lib+'/tensorflow/contrib/layers/python/ops/_sparse_feature_cross_op.so', './tensorflow/contrib/layers/python/ops/'),                       
            (python_lib+'/tensorflow/contrib/coder/python/ops/_coder_ops.so', './tensorflow/contrib/coder/python/ops')]

contr_dir = python_lib+'/atari_py/'
for p1 in pathlib.Path(contr_dir).glob('**/*.so'):
    p1 = str(p1)
    p2 = os.path.join('./atari_py/', os.path.dirname(p1[len(contr_dir):]))
    log.info("Appending binary path ('{}', '{}')".format(p1, p2))
    
    binaries.append((p1, p2))
for p1 in pathlib.Path(contr_dir).glob('**/*.bin'):
    p1 = str(p1)
    p2 = os.path.join('./atari_py/', os.path.dirname(p1[len(contr_dir):]))
    log.info("Appending binary path ('{}', '{}')".format(p1, p2))
    
    binaries.append((p1, p2))


datas=[(python_lib+'/tensorflow/contrib/', './tensorflow/contrib/'), (python_lib+'/atari_py/', './atari_py/')]
"""
hiddenimports = collect_submodules('skimage.io._plugins') \
	      + collect_submodules('sentry_sdk')+ \
	      ['pywt._extensions._cwt','atari_py','gym','gym.envs.atari','networkBuilder',
	       'azure.storage.blob','numpy', 'psutil', 'GPUtil', 'appServer', 'tensorflow',
	       'math', 'sys', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors',
	       'traceback', 'json', 'io', 'struct', 'threading', 'PIL', 'PIL.ImageTk', 'glob',
	       'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'coreCommunicator',
	       'CoreThread', 'core', 'coreLogic', 'data', 'datahandler', 'graph', 'libserver',
	       'environmenthandler', 'qagent','qagent_unity','lw_graph','lw_data','datahandler_lw',
	       'utils', 'code_generator.base', 'code_generator.datadata', 'code_generator.dataenv',
	       'code_generator.__init__', 'code_generator.tensorflow', 'core_new.api',
	       'core_new.cache', 'core_new.data.base', 'core_new.data.__init__',
	       'core_new.data.policies', 'core_new.errors', 'core_new.extras', 'core_new.history',
	       'core_new.lightweight', 'core_new.session', 'core_new.utils', 'core_new.networkCache',
	       'analytics.handlers', 'analytics.scraper',
	       'propegateNetwork','tensorflow.python.eager.context','tensorflow.lite',
	       'tensorflow.lite.toco','tensorflow.lite.toco_convert','tensorflow_wrap_toco',
	       'tensorflow.lite.toco.python','tensorflow.lite.toco.python.tensorflow_wrap_toco',
               '_tensorflow_wrap_toco', 'extractVariables', 'createDataObject', 'tensorflow.contrib',
               'ast', 'itertools', 'collections', 'operator', 'parse_pb', 'functionParser',
               'tensorflow.python', 'networkx', 'tensorflow.python.platform', 'google.protobuf',
               'tensorflow.core.protobuf', 'tensorflow.python.training', 'funclib',
               'tensorflow.lite.toco.python.tensorflow_wrap_toco', '_tensorflow_wrap_toco', 'boto3']
"""

'''
hiddenimports = collect_submodules('skimage.io._plugins') \
	      + collect_submodules('sentry_sdk')+ \
	      ['pywt._extensions._cwt','atari_py','gym','gym.envs.atari','networkBuilder',
	       'azure.storage.blob','numpy', 'psutil', 'GPUtil', 'appServer', 'tensorflow',
	       'math', 'sys', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors',
	       'traceback', 'json', 'io', 'struct', 'threading', 'PIL', 'PIL.ImageTk', 'glob',
	       'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'coreCommunicator',
	       'CoreThread', 'core', 'coreLogic', 'data', 'datahandler', 'graph', 'libserver',
	       'environmenthandler', 'qagent','qagent_unity','lw_graph','lw_data','datahandler_lw',
	       'utils', 'code_generator.base', 'code_generator.datadata', 'code_generator.dataenv',
	       'code_generator.__init__', 'code_generator.tensorflow', 'core_new.api',
	       'core_new.cache', 'core_new.data.base', 'core_new.data.__init__',
	       'core_new.data.policies', 'core_new.errors', 'core_new.extras', 'core_new.history',
	       'core_new.lightweight', 'core_new.session', 'core_new.utils', 's3buckets'
	       'analytics.handlers', 'analytics.scraper', 'dataKeeper', 'codeHQKeeper',
	       'networkExporter', 'appQueue', 'networkSaver', 'databundle', 'modules',
	       'propegateNetwork','tensorflow.python.eager.context','tensorflow.lite',
	       'tensorflow.lite.toco','tensorflow.lite.toco_convert','tensorflow_wrap_toco',
	       'tensorflow.lite.toco.python','tensorflow.lite.toco.python.tensorflow_wrap_toco',
               '_tensorflow_wrap_toco', 'extractVariables', 'createDataObject', 'tensorflow.contrib',
               'ast', 'itertools', 'collections', 'operator', 'parse_pb', 'functionParser',
               'tensorflow.python', 'networkx', 'tensorflow.python.platform', 'google.protobuf',
               'tensorflow.core.protobuf', 'tensorflow.python.training', 'funclib',
               'tensorflow.lite.toco.python.tensorflow_wrap_toco', '_tensorflow_wrap_toco', 'boto3']
'''

hiddenimports=collect_submodules('skimage.io._plugins')+collect_submodules('tensorflow.contrib')+collect_submodules('sentry_sdk')+['pywt._extensions._cwt','databundle','core_new.data.policies','utils','core_new.networkCache','core_new.data.base','core_new.data','core_new.errors','core_new.extras','atari_py','gym','analytics.handlers','analytics.scraper','core_new','core_new.cache','core_new.api','core_new.control','modules','core_new.core','core_new.history','core_new.data','core_new.lightweight','core_new.execution','core_new.resuts','core_new.session','core_new.utils','code_generator.__init__','code_generator.base','code_generator.datadata','code_generator.dataenv','code_generator.tensorflow','core_new.history','s3buckets','S3BucketAdapter','boto3','tempfile','code_generator','codeHQKeeper','datadata_generator','dataKeeper','createDataObject','networkExporter','appQueue','networkSaver','GPUtil','networkBuilder','gym.envs.atari','azure.storage.blob','numpy', 'tensorflow', 'math', 'sys', 'ast', 'itertools', 'collections', 'operator', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors', 'traceback', 'json', 'io', 'struct', 'threading', 'PIL', 'PIL.ImageTk', 'glob', 'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'coreCommunicator', 'CoreThread', 'funclib', 'core', 'coreLogic', 'data', 'datahandler', 'graph', 'parse_pb', 'functionParser', 'extractVariables', 'tensorflow.python', 'libserver', 'networkx', 'environmenthandler', 'appServer', 'qagent','qagent_unity','lw_graph','lw_data','datahandler_lw','propegateNetwork','tensorflow.python.eager.context','tensorflow.lite','tensorflow.lite.toco','tensorflow.lite.toco_convert','tensorflow_wrap_toco','tensorflow.lite.toco.python','tensorflow.python.platform','google.protobuf','tensorflow.core.protobuf','tensorflow.python.training','tensorflow.lite.toco.python.tensorflow_wrap_toco','_tensorflow_wrap_toco']


log.info("pathex = {}".format(pformat(pathex)))
log.info("binaries = {}".format(pformat(binaries)))
log.info("datas = {}".format(pformat(datas)))
log.info("hiddenimports = {}".format(pformat(hiddenimports)))

a = Analysis(['mainServer.py'],
             pathex=pathex,
             binaries=binaries,
             datas=binaries,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False)
#cipher=block_cipher

pyz = PYZ(a.pure, a.zipped_data)
#cipher=block_cipher

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='appServer',
          debug=True,
          strip=False,
          upx=True,
          console=True,icon='favicon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='appServer')

