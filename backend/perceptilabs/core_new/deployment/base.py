import time
import logging
import tempfile
import threading
import subprocess
import importlib.util
from typing import Dict
from abc import ABC, abstractmethod


from perceptilabs.core_new.communication.base import Client
from perceptilabs.core_new.communication.status import STATUS_READY

log = logging.getLogger(__name__)


class DeploymentError(Exception):
    pass


class DeploymentPipe(ABC):

    PORT_OFFSET = 5678
    config_table = {}
    
    # Should have a worker thread that takes care of uploading/downloading files [exported models, weight files, checkpoints, etc]    
    
    @abstractmethod
    def deploy(self, graph, session_id: str):            
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        pass

    def on_receive_file(self):
        # e.g., exported models etc...
        pass

    def on_send_file(self):
        # When file upload is complete..
        pass

    def send_file(self):
        pass

    def _establish_communication(self, config, timeout):
        client = Client(config)

        t0 = time.time()
        ready = False        
        errors = []
        
        while t0 - time.time() < timeout:
            try:
                if client.status == STATUS_READY:
                    ready = True
                    break
            except Exception as e:
                log.error('error ' +repr(e))
                errors.append(e)
            time.sleep(0.3)

        if not ready:
            log.error('Errors during deployment: ' + str(errors))            
            raise DeploymentError('Timeout: deployed script did not indicate status "ready".')

        # If we reached this point, everything went fine.
        return client


    def get_session_config(self, session_id: str) -> Dict[str, str]:

        print(session_id, type(session_id), self.config_table)

        if session_id not in self.config_table:
            n_sessions = len(self.config_table)
            flask_port = self.PORT_OFFSET + 2 * n_sessions
            zmq_port = self.PORT_OFFSET + 2 * n_sessions + 1            
            
            self.config_table[session_id] = {
                'session_id': session_id,
                'addr_flask': f'http://localhost:{flask_port}',
                'port_flask': f'{flask_port}',            
                'addr_zmq': f'tcp://localhost:{zmq_port}',
                'addr_zmq_deploy': f'tcp://*:{zmq_port}'            
            }            
        return self.config_table[session_id].copy()

class InProcessDeploymentPipe(DeploymentPipe):
    def __init__(self, script_factory):
        self._script_factory = script_factory        

    def deploy(self, graph, session_id: str, timeout=10):
        config = self.get_session_config(session_id)
        code, line_to_node_map = self._script_factory.make(graph, config)


        self._line_to_node_map = line_to_node_map # TODO: inject script_factory instead of exposing this here
        
        with open('deploy.py', 'wt') as f:
            f.write(code)
            f.flush()

            import shutil            

            spec = importlib.util.spec_from_file_location("deployed_module", f.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._thread = threading.Thread(target=module.main, kwargs={'wait': True}, daemon=True)
            self._thread.start()

        return self._establish_communication(config, timeout)
        
    @property
    def is_active(self):
        #return self._thread.is_alive()
        return True

    

class LocalEnvironmentPipe(DeploymentPipe):
    def __init__(self, interpreter: str, script_factory):
        self._script_factory = script_factory
        self._interpreter = interpreter
        self._p = None

    def deploy(self, graph, session_id: str):        
        code = self._script_factory.make(
            graph,
            self.get_session_config(session_id)
        )
        
        with tempfile.NamedTemporaryFile(suffix='.py', mode='wt') as f:
            # TODO: fix for windows!
            f.write(code)
            f.flush()

            import shutil
            shutil.copy(f.name, 'deploy.py')

            path = f.name
            threading.Thread(target=self._deploy, args=(path,), daemon=True).start()
            

    def _deploy(self, script_path):
        self._p = subprocess.Popen(
            [self._interpreter, 'deploy.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = self._p.communicate()
        log.debug(f"Deployment returned:\nstdout: {stdout}\nstderr: {stderr}")
            
    @property
    def is_active(self):
        if self._p is None or self._p.poll() is not None:
            return False
        return True

