import inspect
import importlib


class InvalidPathError(Exception):
    pass


class ObjectHook:
    def __init__(self, target, hook, include_vars=False):
        self._target = target
        self._hook = hook
        self._include_vars = include_vars

    def __call__(self, *args, **kwargs):
        if self._include_vars:
            prev_frame = inspect.currentframe().f_back
            globals_ = prev_frame.f_globals.copy()
            locals_ = prev_frame.f_locals.copy()
        else:
            globals_, locals_ = None, None
            
        return self._hook(self._target, globals_, locals_, *args, **kwargs)

    def __repr__(self):
        return "{} rerouting {} via {}".format(self.__class__.__name__, self._target, self._hook)
    
    @property
    def target(self):
        return self._target
    

class ObjectProxy:
    def __init__(self, target):
        self._target = target
        self._hooks = {}

    def __getattr__(self, name):
        attr = self._hooks.get(name)
        if attr is None:
            attr = getattr(self._target, name)
        return attr
        
    def install_hook(self, target_path, hook_func, include_vars=False):
        split = target_path.split('.', 1)

        if len(split) == 1:
            target_name = split[0]
            target = getattr(self, target_name)
            self._hooks[target_name] = ObjectHook(target, hook_func, include_vars)
        elif len(split) > 1:
            first_name, remaining_path = split
            attr = getattr(self, first_name)
            
            if attr is None:
                raise InvalidPathError                
            elif isinstance(attr, ObjectProxy):
                proxy = attr
            else:
                proxy = ObjectProxy(attr)
                setattr(self, first_name, proxy)

            proxy.install_hook(remaining_path, hook_func, include_vars)
        else:
            raise InvalidPathError

    def __repr__(self):
        text  = self.__class__.__name__ + " of " + repr(self._target)
        return text

    @property
    def target(self):
        return self._target

    
class ModuleProvider:
    def __init__(self):
        self._modules = {}
        self._hooks = {}
        
    def load(self, name, as_name=None):
        if as_name is None:
            as_name = name

        module = importlib.import_module(name)
        self._modules[as_name] = ObjectProxy(module)

    def install_hook(self, target_path, hook_func, include_vars=False):
        module_name, remaining_path = target_path.split('.', 1)
        try:
            self._modules[module_name].install_hook(remaining_path, hook_func, include_vars)
            self._hooks[target_path] = hook_func
        except InvalidPathError:
            raise ValueError("Invalid path: '{}'".format(target_path))
        except:
            raise

    # def uninstall_hooks(self):
    #     for key in self._modules.keys():
    #         self._modules[target_path] = self._modules[target_path].target                            

    @property
    def modules(self):
        return self._modules.copy()
        
    @property
    def hooks(self):
        return self._hooks.copy()

    def __getitem__(self, name):
        return self._modules[name]    

    
if __name__ == "__main__":

    def hook_func(target, globals_, locals_, *args, **kwargs):
        print("Hello from hook on " + repr(target))
        return target(*args, **kwargs)
        
    
    #import tensorflow as tf

    mp = ModuleProvider()
    mp.load('tensorflow', 'tf')

    tf_ = mp['tf']
    print(tf_)
    
    mp.install_hook('tf.placeholder', hook_func)
    mp.install_hook('tf.nn.relu', hook_func)    
    tf_ = mp['tf']
    print(tf_.nn)
    
    X = tf_.placeholder(tf_.float32)
    Y = tf_.nn.relu(X)

    print(X, Y)

    import tensorflow as tf

    print(tf.placeholder)
    print(tf_.placeholder)    

    
