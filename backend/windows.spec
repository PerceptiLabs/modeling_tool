# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("skimage.io._plugins")

#block_cipher = pyi_crypto.PyiBlockCipher(key='sjdielskaospelsk')
#('C:\\Users\\Robert\\Anaconda3\\Lib\\site-packages\\ale_c.cp36-win_amd64.dll','.'),


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

pathex = [working_dir]

#, (python_lib+'/tensorflow/python/_pywrap_tensorflow_internal.pyd', '.')

binaries = [(python_lib+'/ale_c.cp36-win_amd64.dll','.'), (python_lib+'/dask/dask.yaml','./dask/'), (python_lib+'/sklearn/.libs/vcomp140.dll', './sklearn/.libs/')]

python_files = []
with open('../../backend/included_files.txt') as f:
    for line in f:
        tmp_line = line.strip()
        if "#" not in tmp_line and tmp_line and tmp_line.endswith(".py"):
            python_files.append(".".join(tmp_line.split(".")[:-1]).replace("/","."))

print("Found these python modules to include: " + str(python_files))
hiddenimports = collect_submodules('skimage.io._plugins') + collect_submodules('tensorflow.contrib') + collect_submodules('sentry_sdk') + python_files + \
            ['pywt._extensions._cwt','databundle','atari_py','gym','boto3','tempfile','jinja2','pkg_resources.py2_warn', 'cryptography.fernet',
            'GPUtil','gym.envs.atari','azure.storage.blob','numpy', 'tensorflow', 'math', 'sys', 'ast', 'itertools', 
            'collections', 'operator', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors', 'traceback', 'json', 'io', 'struct', 'threading', 'PIL',
            'PIL.ImageTk', 'glob', 'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'tensorflow.python','networkx', 
            'tensorflow.python.eager.context','tensorflow.lite','tensorflow.lite.toco',
            'tensorflow.lite.toco_convert','tensorflow_wrap_toco','tensorflow.lite.toco.python','tensorflow.python.platform','google.protobuf','tensorflow.core.protobuf',
            'tensorflow.python.training','tensorflow.lite.toco.python.tensorflow_wrap_toco','_tensorflow_wrap_toco', 'pkg_resources.py2_warn', 'dill', 'zmq']

datas  =[
    (python_lib+'/tensorflow/contrib/', './tensorflow/contrib/'),
    (python_lib+'/atari_py/', './atari_py/'),
    (working_dir+'/perceptilabs/insights/csv_ram_estimator/model_and_meta.pkl', './perceptilabs/insights/csv_ram_estimator/'),
    (working_dir+'/perceptilabs/app_variables.json','./perceptilabs/'),
    (working_dir+'/perceptilabs/script/templates/', './perceptilabs/script/templates/'),
]


log.info("pathex = {}".format(pformat(pathex)))
log.info("binaries = {}".format(pformat(binaries)))
log.info("datas = {}".format(pformat(datas)))
log.info("hiddenimports = {}".format(pformat(hiddenimports)))

a = Analysis(['main.py'],
             pathex=pathex,
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4','QtCore','PyQt5','Matplotlib', 'babel'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False)
             
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='appServer',
          debug=True,
          strip=False,
          upx=True,
          console=True)#,icon='favicon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='appServer')

