# -*- mode: python -*-

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
#import distutils
#if distutils.distutils_path.endswith('__init__.py'):
#    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("skimage.io._plugins")

#block_cipher = pyi_crypto.PyiBlockCipher(key='sjdielskaospelsk')
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
          python_lib+'/tensorflow',
          python_lib+'/atari_py']

*    (working_dir+'/appServer.cpython-36m-darwin.so', '.'),
binaries = [
    (working_dir+'/s3buckets.cpython-36m-darwin.so', '.'),
    (working_dir+'/analytics/handlers.cpython-36m-darwin.so', './analytics'),        
    (python_lib+'/tensorflow/contrib/bigtable/python/ops/_bigtable.so', './tensorflow/contrib/bigtable/python/ops'),
    (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
    (python_lib+'/tensorflow/contrib/rnn/python/ops/_gru_ops.so', './tensorflow/contrib/rnn/python/ops/'),
    (python_lib+'/tensorflow/contrib/tpu/python/ops/_tpu_ops.so', './tensorflow/contrib/tpu/python/ops'),
    (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),
    (python_lib+'/tensorflow/contrib/factorization/python/ops/_clustering_ops.so', './tensorflow/contrib/factorization/python/ops'),
    (python_lib+'/tensorflow/contrib/input_pipeline/python/ops/_input_pipeline_ops.so', './tensorflow/contrib/input_pipeline/python/ops/'),                       
    (python_lib+'/tensorflow/contrib/rnn/python/ops/_lstm_ops.so', './tensorflow/contrib/rnn/python/ops/'),
    (python_lib+'/tensorflow/contrib/layers/python/ops/_sparse_feature_cross_op.so', './tensorflow/contrib/layers/python/ops/'),                       
    (python_lib+'/tensorflow/contrib/coder/python/ops/_coder_ops.so', './tensorflow/contrib/coder/python/ops'),
    (python_lib+'/atari_py/ale_interface/libale_c.so', './atari_py/ale_interface/')
]


#contr_dir = python_lib+'/atari_py/'
#for p1 in pathlib.Path(contr_dir).glob('**/*.bin'):
#    p1 = str(p1)
#    p2 = os.path.join('./atari_py/', os.path.dirname(p1[len(contr_dir):]))
#    log.info("Appending binary path ('{}', '{}')".format(p1, p2))
#    
#    binaries.append((p1, p2))


datas=[
    (python_lib+'/tensorflow/contrib/', './tensorflow/contrib/'),
    (python_lib+'/dask/dask.yaml', './dask/'),
    (python_lib+'/atari_py/atari_roms/breakout.bin', './atari_py/atari_roms/'),
    (python_lib+'/atari_py/atari_roms/bank_heist.bin', './atari_py/atari_roms/'),
    (python_lib+'/atari_py/atari_roms/demon_attack.bin', './atari_py/atari_roms/'),
    ('app_variables.json','.')  
]       



python_files = []
with open('../../backend/included_files.txt') as f:
    for line in f:
        if "#" not in line and line.strip():
            python_files.append(".".join(line.strip().split(".")[:-1]).replace("/","."))

print("Found these python modules to include: " + str(python_files))
hiddenimports = collect_submodules('skimage.io._plugins') + collect_submodules('tensorflow') + collect_submodules('sentry_sdk') + python_files + \
            ['pywt._extensions._cwt','databundle','atari_py','gym','boto3','tempfile', 'astor',
            'GPUtil','gym.envs.atari','azure.storage.blob','numpy', 'tensorflow', 'math', 'sys', 'ast', 'itertools', 
            'collections', 'operator', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors', 'traceback', 'json', 'io', 'struct', 'threading', 'PIL',
            'PIL.ImageTk', 'glob', 'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'tensorflow.python','networkx', 
            'tensorflow.python.eager.context','tensorflow.lite','tensorflow.lite.toco',
            'tensorflow.lite.toco_convert','tensorflow_wrap_toco','tensorflow.lite.toco.python','tensorflow.python.platform','google.protobuf','tensorflow.core.protobuf',
            'tensorflow.python.training','tensorflow.lite.toco.python.tensorflow_wrap_toco','_tensorflow_wrap_toco']


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
