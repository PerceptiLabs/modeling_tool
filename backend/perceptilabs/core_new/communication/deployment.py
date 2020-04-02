from abc import abstractmethod, ABC
import threading
import subprocess


class DeploymentStrategy(ABC):
    @abstractmethod
    def run(self, path):
        raise NotImplementedError


class SubprocessStrategy(DeploymentStrategy):
    def __init__(self, interpreter):
        self._interpreter = interpreter
        
    def run(self, path):
        #multiprocessing.Process # Not a good idea. Uses FORK and that causes tensorflow issues. Spawn requires pickling..  https://github.com/tensorflow/tensorflow/issues/5448                    
        p = subprocess.Popen(
            [interpreter, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


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
        thread = threading.Thread(target=self._fn_start, args=(path,), daemon=True)
        thread.start()
    
