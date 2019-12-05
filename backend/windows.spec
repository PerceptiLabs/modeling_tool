# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

#from common import hiddenimports

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

binaries = [(python_lib+'/dask/dask.yaml','./dask/')]

python_files = []
with open('../../scripts/included_files.txt') as f:
    for line in f:
        if "#" not in line and line.strip():
            python_files.append(".".join(line.strip().split(".")[:-1]).replace("/","."))

print("Found these python files to include: " + str(python_files))

datas=[(python_lib+'/tensorflow/contrib/', './tensorflow/contrib/'), (python_lib+'/dask/dask.yaml', './dask/')]
hiddenimports = collect_submodules('skimage.io._plugins') + collect_submodules('tensorflow.contrib') + collect_submodules('sentry_sdk') + python_files + \
            ['pywt._extensions._cwt','databundle','atari_py','gym','boto3','tempfile',
            'GPUtil','gym.envs.atari','azure.storage.blob','numpy', 'tensorflow', 'math', 'sys', 'ast', 'itertools', 
            'collections', 'operator', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors', 'traceback', 'json', 'io', 'struct', 'threading', 'PIL',
            'PIL.ImageTk', 'glob', 'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'tensorflow.python','networkx', 
            'tensorflow.python.eager.context','tensorflow.lite','tensorflow.lite.toco',
            'tensorflow.lite.toco_convert','tensorflow_wrap_toco','tensorflow.lite.toco.python','tensorflow.python.platform','google.protobuf','tensorflow.core.protobuf',
            'tensorflow.python.training','tensorflow.lite.toco.python.tensorflow_wrap_toco','_tensorflow_wrap_toco']

#['pywt._extensions._cwt','databundle','core_new.data.policies','utils','core_new.networkCache','core_new.data.base','core_new.data','core_new.errors','core_new.extras','atari_py','gym','analytics.handlers','analytics.scraper','core_new','core_new.cache','core_new.api','core_new.control','modules','core_new.core','core_new.history','core_new.data','core_new.lightweight','core_new.execution','core_new.resuts','core_new.session','core_new.utils','code_generator.__init__','code_generator.base','code_generator.datadata','code_generator.dataenv','code_generator.tensorflow','core_new.history','s3buckets','S3BucketAdapter','boto3','tempfile','code_generator','codeHQKeeper','datadata_generator','dataKeeper','createDataObject','networkExporter','appQueue','networkSaver','GPUtil','networkBuilder','gym.envs.atari','azure.storage.blob','numpy', 'tensorflow', 'math', 'sys', 'ast', 'itertools', 'collections', 'operator', 'time', 'copy', 'queue', 'sklearn.cluster', 'socket', 'selectors', 'traceback', 'json', 'io', 'struct', 'threading', 'PIL', 'PIL.ImageTk', 'glob', 'random', 'os.path', 're', 'codehq', 'dask', 'skimage.io', 'coreCommunicator', 'CoreThread', 'funclib', 'core', 'coreLogic', 'data', 'datahandler', 'graph', 'parse_pb', 'functionParser', 'extractVariables', 'tensorflow.python', 'libserver', 'networkx', 'environmenthandler', 'appServer', 'qagent','qagent_unity','lw_graph','lw_data','datahandler_lw','propegateNetwork','tensorflow.python.eager.context','tensorflow.lite','tensorflow.lite.toco','tensorflow.lite.toco_convert','tensorflow_wrap_toco','tensorflow.lite.toco.python','tensorflow.python.platform','google.protobuf','tensorflow.core.protobuf','tensorflow.python.training','tensorflow.lite.toco.python.tensorflow_wrap_toco','_tensorflow_wrap_toco']

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

log.info("pathex = {}".format(pformat(pathex)))
log.info("binaries = {}".format(pformat(binaries)))
log.info("datas = {}".format(pformat(datas)))
log.info("hiddenimports = {}".format(pformat(hiddenimports)))

#a = Analysis(['mainServer.py'],
#             pathex=pathex,
#             binaries=binaries,
#             datas=datas,
#             hiddenimports=hiddenimports,
#             hookspath=[],
#             runtime_hooks=[],
#             excludes=['PyQt4','QtCore','PyQt5','Matplotlib', 'babel'],
#             win_no_prefer_redirects=False,
#             win_private_assemblies=False,
#             cipher=block_cipher)
#             
#pyz = PYZ(a.pure, a.zipped_data,
#             cipher=block_cipher)

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

#######################################
# Code-sign the generated executable
#import subprocess
#try:
#   subprocess.call([
#      "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe", "sign",
#      "/tr", "http://timestamp.digicert.com",
#      "/td", "sha256",
#      "/fd", "sha256",
#      "C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/compileServer/dist/appServer/appServer.exe",
#   ])
#except:
#   print("Code signing failed")
#   import traceback
#   print(traceback.format_exc())
#######################################
