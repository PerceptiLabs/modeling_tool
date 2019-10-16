from code_generator import CodeGenerator


class DataEnvironmentCodeGenerator(CodeGenerator):
    def __init__(self, environment_name):
        self._env_name = environment_name
    
    def get_code(self):
        code  = "global state_tensor, env\n"
        code += "state_tensor = tf.placeholder(tf.float32, name='state_tensor')\n"        
        code += "env = gym.make(%s)\n" % self._env_name
        code += "\n"
        code += "sample = env.reset()\n"
        code += "api.data.store(sample=_sample)\n"
        code += "Y = state_tensor\n"        
        return code


    
