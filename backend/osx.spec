# -*- mode: python -*-

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
#import distutils
#if distutils.distutils_path.endswith('__init__.py'):
#    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("skimage.io._plugins")

block_cipher = pyi_crypto.PyiBlockCipher(key='sjdielskaospelsk')
#block_cipher = None
#('C:\\Users\\Robert\\Anaconda3\\Lib\\site-packages\\ale_c.cp36-win_amd64.dll','.'),
#('C:/Users/Robert/Anaconda3/envs/baseCore/Lib/site-packages/dask/dask.yaml','./dask/'),('C:\\Users\\Robert\\Anaconda3\\envs\\baseCore\\Lib\\site-packages\\tensorflow\\lite\\toco\\python\\_tensorflow_wrap_toco.pyd','.')
#('C:\\Users\\Robert\\Anaconda3\\envs\\baseCore\\Lib\\site-packages\\atari_py','atari_py')
#binaries=[('/Users/robert/Downloads/macServer/compiled/appServer.cpython-36m-darwin.so','.'),('/anaconda3/envs/baseCore/lib/python3.6/site-packages/tensorflow/python/_pywrap_tensorflow_internal.so','./site-packages/tensorflow/python'),('/anaconda3/envs/baseCore/lib/python3.6/site-packages/atari_py/ale_interface/libale_c.so','./atari_py/ale_interface'),('/anaconda3/envs/baseCore/lib/python3.6/site-packages/tensorflow/contrib/bigtable/python/ops/_bigtable.so','./tensorflow/contrib/bigtable/python/ops')],



import pathlib
import os
from distutils.sysconfig import get_python_lib
from pprint import pformat
from logging import getLogger
log = getLogger(__name__)


working_dir = os.getcwd()
log.info("working_dir = " + working_dir)

python_lib = get_python_lib()
log.info("python_lib = " + python_lib)


pathex = [working_dir,
          python_lib+'/tensorflow']

binaries = [(working_dir+'/appServer.cpython-36m-darwin.so', '.'),
            (python_lib+'/tensorflow/contrib/bigtable/python/ops/_bigtable.so', './tensorflow/contrib/bigtable/python/ops'),
            (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
            (python_lib+'/tensorflow/contrib/rnn/python/ops/_gru_ops.so', './tensorflow/contrib/rnn/python/ops/'),
            (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
            (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),
            (python_lib+'/tensorflow/contrib/factorization/python/ops/_clustering_ops.so', './tensorflow/contrib/factorization/python/ops'),
            (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),                       
            (python_lib+'/tensorflow/contrib/rnn/python/ops/_lstm_ops.so', './tensorflow/contrib/rnn/python/ops/'),
            (python_lib+'/tensorflow/contrib/layers/python/ops/_sparse_feature_cross_op.so', './tensorflow/contrib/layers/python/ops/'),                       
            (python_lib+'/tensorflow/contrib/coder/python/ops/_coder_ops.so', './tensorflow/contrib/coder/python/ops')]


datas=[(python_lib+'/tensorflow/contrib/', './tensorflow/contrib/'), (python_lib+'/dask/dask.yaml', './dask/')]


hiddenimports = collect_submodules('skimage.io._plugins') \
	      + collect_submodules('sentry_sdk')+ \
	      ['pywt._extensions._cwt','atari_py','gym','gym.envs.atari','networkBuilder',
	       'azure.storage.blob','numpy', 'psutil', 'GPUtil', 'appServer', 'tensorflow',
	       'math', 'sys', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors',
	       'traceback', 'json', 'io', 'struct', 'threading', 'PIL', 'PIL.ImageTk', 'glob',
	       'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'coreCommunicator',
	       'CoreThread', 'core', 'coreLogic', 'data', 'datahandler', 'graph', 'libserver',
	       'environmenthandler', 'qagent','qagent_unity','lw_graph','lw_data','datahandler_lw',
	       'propegateNetwork','tensorflow.python.eager.context','tensorflow.lite',
	       'tensorflow.lite.toco','tensorflow.lite.toco_convert','tensorflow_wrap_toco',
	       'tensorflow.lite.toco.python','tensorflow.lite.toco.python.tensorflow_wrap_toco',
               '_tensorflow_wrap_toco', 'extractVariables', 'createDataObject', 'tensorflow.contrib',
               'ast', 'itertools', 'collections', 'operator', 'parse_pb', 'functionParser',
               'tensorflow.python', 'networkx', 'tensorflow.python.platform', 'google.protobuf',
               'tensorflow.core.protobuf', 'tensorflow.python.training', 'funclib',
               'tensorflow.lite.toco.python.tensorflow_wrap_toco', '_tensorflow_wrap_toco','boto3']

log.info("pathex = {}".format(pformat(pathex)))
log.info("binaries = {}".format(pformat(binaries)))
log.info("datas = {}".format(pformat(datas)))
log.info("hiddenimports = {}".format(pformat(hiddenimports)))
   

a = Analysis(['mainServer.py'],
             pathex=pathex,
	     binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4','QtCore','PyQt5','Matplotlib', 'babel'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
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
