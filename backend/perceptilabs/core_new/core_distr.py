import sys
import copy
import pprint
import logging
import numpy as np
import traceback
import tensorflow as tf
import pandas as pd
from collections import namedtuple
import gym

from perceptilabs.graph import Graph
from perceptilabs.modules import ModuleProvider
from perceptilabs.core_new.api.legacy import Api, DataApi, UiApi
from perceptilabs.core_new.data import DataContainer
from perceptilabs.core_new.core import Core
from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.script_distr import ScriptBuilder
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.core_new.errors import LayerSessionAbort
from perceptilabs.core_new.history import SessionHistory, HistoryInputException
from perceptilabs.core_new.session import LayerSession, LayerSessionStop, LayerIo
from perceptilabs.core_new.data.policies import TrainValDataPolicy, TestDataPolicy, TrainReinforceDataPolicy
from perceptilabs.analytics.scraper import get_scraper

log = logging.getLogger(__name__)
scraper = get_scraper()

class DistributedCore(Core):

    def run(self):
        self._reset()        
        self._print_basic_info()
        
        set_tensorflow_mode('eager' if self._tf_eager else 'graph')
        sb = ScriptBuilder()
        
        full_code = ""
        
        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]

            if self._should_skip_layer(layer_id, content):
                continue


            code_gen = self._codehq.get_code_generator(layer_id, content)            
            log.debug(repr(code_gen))

            sb.layer(f"{layer_id}",
                     code_gen.get_code(),
                     input_layers=content["Con"],
                     checkpoint=None,
                     layer_type=layer_type)
            
        full_code = sb.build()
        print(full_code)

        with open('thescript.py', 'w') as f:

            full_code_extra  = 'import tensorflow as tf\n'
            full_code_extra += 'import numpy as np\n'
            full_code_extra += 'import pandas as pd\n'
            full_code_extra += 'import gym\n'
            full_code_extra += 'import json\n'
            full_code_extra += 'import os\n'
            full_code_extra += 'import os\n'
            full_code_extra += 'import dask.array as da\n'
            full_code_extra += 'import dask.dataframe as dd\n'
            full_code_extra += 'from unittest.mock import MagicMock\n'
            full_code_extra += 'api = MagicMock()\n'
            full_code_extra += 'api.data.get_tensors.return_value = {}\n'
            full_code_extra += 'api.ui.headless = False\n'
            full_code_extra += 'api.ui.skip = False\n'                        
            
            full_code_extra += full_code
            
            f.write(full_code_extra)
        
        
        
        globals_, locals_ = self._get_globals_and_locals(input_layer_ids=[])
        
        session = LayerSession("<no_id>", "<no_type>", full_code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler,
                               cache=self._session_history.cache)   

        try:
            session.run()
        except LayerSessionStop:
            raise # Not an error. Re-raise.
        except Exception as e:
            self._error_handler.handle_run_error(session, e)



    
