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

from graph import Graph
from modules import ModuleProvider
from core_new.api import Api, DataApi, UiApi
from core_new.data import DataContainer
from core_new.core import Core
from core_new.utils import set_tensorflow_mode
from core_new.extras import LayerExtrasReader
from core_new.errors import LayerSessionAbort
from core_new.history import SessionHistory, HistoryInputException
from core_new.session import LayerSession, LayerSessionStop, LayerIo
from core_new.data.policies import TrainValDataPolicy, TestDataPolicy, TrainReinforceDataPolicy
from analytics.scraper import get_scraper

log = logging.getLogger(__name__)
scraper = get_scraper()

class DistributedCore(Core):

    def run(self):
        self._reset()        
        self._print_basic_info()
        
        set_tensorflow_mode('eager' if self._tf_eager else 'graph')


        full_code = ""
        
        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]

            if self._should_skip_layer(layer_id, content):
                continue


            code_gen = self._codehq.get_code_generator(layer_id, content)            
            log.debug(repr(code_gen))

            layer_code  = f"#--------- Layer {layer_id} [{layer_type}] ---------\n"
            layer_code += code_gen.get_code()
            layer_code += "\n\n"
            layer_code = layer_code.replace("global ", "#global ")
            
            full_code += layer_code 

        print(full_code)

        globals_, locals_ = self._get_globals_and_locals(input_layer_ids=[])
        
        session = LayerSession(-1, content['Info']['Type'], full_code,
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

        import pdb; pdb.set_trace()

        if True:
            return

        while True:

            log.info("Preparing layer session with id {} and type {}".format(layer_id, layer_type))
            try:
                self._run_layer(layer_id, content)
            except LayerSessionStop:
                log.info("Stop requested during session {}".format(layer_id))                
                break
            except LayerSessionAbort:
                
                log.info("Error handler aborted session {}".format(layer_id))
                break
            except Exception:
                log.exception("Exception in %s" % layer_id)
                raise


    
