from abc import abstractmethod, ABC
import os
import logging
import threading
import subprocess


from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class DeploymentStrategy(ABC):
    @abstractmethod
    def run(self, path):
        raise NotImplementedError

    @abstractmethod
    def shutdown(self, timeout=None):
        raise NotImplementedError


class SubprocessStrategy(DeploymentStrategy):
    def __init__(self, interpreter):
        self._interpreter = interpreter
        
    def run(self, path):
        #multiprocessing.Process # Not a good idea. Uses FORK and that causes tensorflow issues. Spawn requires pickling..  https://github.com/tensorflow/tensorflow/issues/5448                    
        p = subprocess.Popen(
            [self._interpreter, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
    def shutdown(self, timeout=None):
        raise NotImplementedError

        
class ThreadStrategy(DeploymentStrategy):
    @staticmethod
    def _fn_start(path):
        import importlib            
        with open(path, 'rt') as f:            
            spec = importlib.util.spec_from_file_location("training_module", f.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.main()
    
    def run(self, path):
        self._thread = threading.Thread(target=self._fn_start, args=(path,), daemon=True)
        self._thread.start()
    
    def shutdown(self, timeout=None):
        self._thread.join(timeout=timeout)

        return not self._thread.is_alive() # If thread is dead, success
