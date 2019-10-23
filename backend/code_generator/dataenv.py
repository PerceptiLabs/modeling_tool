from code_generator import CodeGenerator


class DataEnvironmentCodeGenerator(CodeGenerator):
    def __init__(self, environment_name, history_length):
        self._env_name = environment_name
        self._hist_len = history_length
    def get_code(self):
        code  = "global state_tensor, env\n"
        code += "env = gym.make('%s')\n" % self._env_name
        #code += "env = DummyEnv()\n" # TODO: REMOVE THIS WHEN NOT DEBUGGING!!!!
        code += "\n"
        code += "sample = env.reset()\n"
        code += "api.data.store(sample=sample)\n"        
        code += "state_tensor = tf.placeholder(tf.float32, \n"
        code += "                              shape=(None, %s,) + sample.shape,\n" % self._hist_len                
        code += "                              name='state_tensor')\n"       
        code += "Y = state_tensor\n"        
        return code


    
