import imp
import uuid
import inspect
import logging
import importlib
from collections import namedtuple

log = logging.getLogger(__name__)


HookInfo = namedtuple('HookInfo', ['target_path', 'obj'])


class FunctionHook:
    def __init__(self, target, hook, include_vars=False):
        self._target = target
        self._hook = hook
        self._include_vars = include_vars

    def __call__(self, *args, **kwargs):
        if self._include_vars:
            prev_frame = inspect.currentframe().f_back
            globals_ = prev_frame.f_globals.copy()
            locals_ = prev_frame.f_locals.copy()                
            return self._hook(self._target, globals_, locals_, *args, **kwargs)
        else:
            return self._hook(self._target, *args, **kwargs)            

    def __repr__(self):
        return "FunctionHook rerouting {} via {}".format(self._target, self._hook)

    @property
    def target(self):
        return self._target

    
class ModuleProvider:
    def __init__(self):
        self._modules = {}
        self._unsafe_modules = []
        self._hooks = []

    def load(self, name, as_name=None):
        if as_name is None:
            as_name = name
            
        unique_name = name + '_' + uuid.uuid4().hex # If the module is loaded with a generic name,
                                                    # e.g. 'tf', it could interfere with regular import statements
                                                    # Caution: uuid is not truly unique, but it should be close enough
        try:
            self._modules[as_name] = imp.load_module(unique_name, *imp.find_module(name))
        except Exception as e:
            log.warning("Failed importing '{}' using imp.load_module. Reason: {}".format(name, repr(e)))
            log.info("Falling back to importlib.import_module for '{}'.".format(name))
            self._modules[as_name] = importlib.import_module(name)
            self._unsafe_modules.append(as_name)

    def install_hook(self, target_path, hook_func, include_vars=False):
        root_module = target_path.split('.')[0]        
        parent_attr, target_name, target_func  = self._find_target(target_path)

        if root_module in self._unsafe_modules:
            log.warning("Module {} has been marked unsafe for hooking since it was imported using importlib. Hooking its members may have unexpected consequences!")
    
        hook_obj = FunctionHook(target_func, hook_func, include_vars)
        setattr(parent_attr, target_name, hook_obj)
        
        hook_info = HookInfo(target_path, hook_obj)
        self._hooks.append(hook_info)
        
    def uninstall_hooks(self):
        while len(self._hooks) > 0:
            hook_info = self._hooks.pop(0)
            parent_attr, target_name, _ = self._find_target(hook_info.target_path)
            setattr(parent_attr, target_name, hook_info.obj.target)

    def _find_target(self, target_path):
        split_path = target_path.split('.')

        module_name = split_path[0]
        target_name = split_path[-1]

        parent_attr = self._modules.get(module_name) 
        for name in split_path[1:-1]: # Find the correct submodule
            parent_attr = getattr(parent_attr, name)
                
        target_func = getattr(parent_attr, target_name)
        return parent_attr, target_name, target_func

    @property
    def modules(self):
        return self._modules.copy()

    @property
    def hooks(self):
        return self._hooks.copy()


if __name__ == "__main__":
    def placeholder_hook(func, *args, **kwargs):
        print("HELLO FROM PLACEHOLDER!")
        #return func(*args, **kwargs)
        import numpy as np
        import tensorflow as tf
        
        value = np.ones(kwargs['shape'])
        return tf.constant(value)
        
    
    def relu_hook(func, *args, **kwargs):
        print("HELLO FROM RELU!")
        return func(*args, **kwargs)

    import tensorflow as tf
    print(tf.placeholder)

    mp = ModuleProvider()
    mp.load('tensorflow', as_name='tf')

    print("LIGHTWEIGHT CORE RUN")    
    mp.install_hook('tf.placeholder', placeholder_hook)
    mp.install_hook('tf.nn.relu', relu_hook)        
    g = mp.modules

    print(tf.placeholder)
    print(tf.nn.relu)    

    code  = "x = tf.placeholder(tf.float32, shape=[32, 32])\n"
    code += "y = tf.nn.relu(x)\n"
    code += "print(x, y)\n"
    exec(code, g)

    print("FULL CORE RUN")
    mp.uninstall_hooks()
    g = mp.modules

    print(tf.placeholder)
    print(tf.nn.relu)    

    code  = "x = tf.placeholder(tf.float32, shape=[32, 32])\n"            
    code += "y = tf.nn.relu(x)\n"
    code += "print(x, y)\n"
    exec(code, g)
    


