import time
import threading
import tempfile
import subprocess
import importlib.util
from typing import Dict
from abc import ABC, abstractmethod


class DeploymentPipe(ABC):
    # Should have a worker thread that takes care of uploading/downloading files [exported models, weight files, checkpoints, etc]    
    
    @abstractmethod
    def deploy(self, graph, session_id: str):            
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def get_session_config(self, session_id: str) -> Dict[str, str]:
        pass

    def on_receive_file(self):
        # e.g., exported models etc...
        pass

    def on_send_file(self):
        # When file upload is complete..
        pass

    def send_file(self):
        pass
    
class InProcessDeploymentPipe(DeploymentPipe):
    def __init__(self, script_factory):
        self._script_factory = script_factory        

    def deploy(self, graph, session_id: str):
        code = self._script_factory.make(
            graph,
            self.get_session_config(session_id)
        )
        
        with open('deploy.py', 'wt') as f:
            f.write(code)
            f.flush()

            import shutil            

            spec = importlib.util.spec_from_file_location("deployed_module", f.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._thread = threading.Thread(target=module.main, args=(), daemon=True)
            self._thread.start()

    @property
    def is_active(self):
        #return self._thread.is_alive()
        return True

    def get_session_config(self, session_id: str) -> Dict[str, str]:
        return {
            'session_id': session_id,
            'ip_addr': '<nothing here yet>'
        }
    


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
            f.write(code)
            f.flush()

            import shutil
            shutil.copy(f.name, 'deploy.py')


            
            self._p = subprocess.Popen(
                [self._interpreter, 'deploy.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            #out, err = self._p.communicate()
            #print(out, err)
            #import pdb; pdb.set_trace()
            
    @property
    def is_active(self):
        if self._p is None or self._p.poll() is not None:
            return False
        return True

    def get_session_config(self, session_id: str) -> Dict[str, str]:
        return {
            'session_id': session_id,
            'ip_addr': '<nothing here yet>'
        }
    
