import tensorflow as tf
from qagent import QAgent
from qagent_unity import QAgentUnity
import numpy as np

#from a2cagent import A2CAgent
#from subproc_vec_env import SubprocVecEnv

class EnvironmentHandler():
    def __init__(self,accessProperties):
        self.FLAG_UNITY=False
        self.env=self.readEnvironment(accessProperties)
        self.sample=self.getSample()
        self.data_size=1
        self.batch_size=int(accessProperties["Batch_size"])
        self.placeholders={}

    def readEnvironment(self, accessProperties):
        if accessProperties['EnvType']=="Gym":
            import gym
            #env=SubprocVecEnv([gym.make(accessProperties['Atari']+'-v0'),gym.make(accessProperties['Atari']+'-v0'),gym.make(accessProperties['Atari']+'-v0')])
            env=gym.make(accessProperties['Atari']+'-v0')
        elif accessProperties['EnvType']=="Unity":
            self.FLAG_UNITY=True
            from unityagents import UnityEnvironment
            env=UnityEnvironment(file_name=accessProperties["Path"])
        return env

    def prepareEnvironment(self):
        dimensions=np.shape(self.sample)
        #Returns a placeholder with the correct size for the data
        dimLen=len(dimensions)+1
        if dimLen<=1:
            return tf.placeholder(tf.float32, shape=[None])
        else:
            #return tf.placeholder(tf.float32, shape=[None for dim in range(dimLen-1)]+[dimensions[-1]])
            return tf.placeholder(tf.float32, shape=[None]+[dim for dim in dimensions])

    def setAgent(self, reinforce_type, action_string, safe_dict, workerDict, outputVariables, graph):
        if reinforce_type=="Q_learning":
            if self.FLAG_UNITY:
                self.agent=QAgentUnity(self.env, action_string, safe_dict, workerDict, outputVariables, graph, self.batch_size)
            else:
                self.agent=QAgent(self.env, action_string, safe_dict, workerDict, outputVariables, graph, self.batch_size)
            self.placeholders['Action']=tf.placeholder(tf.float32, shape=[None,self.getActionSpace()])
            self.placeholders['Reward']=tf.placeholder(tf.float32, shape=[None])
            self.placeholders['Target']=tf.placeholder(tf.float32, shape=[None,self.getActionSpace()])
            self.placeholders['Done']=tf.placeholder(tf.bool, shape=[None])
        elif reinforce_type=='Policy_gradient':
            #self.agent=PolicyAgent()
            pass
        elif reinforce_type=='A2C':
            #self.agent=A2CAgent(self.env, action_string, safe_dict, workerDict, outputVariables, graph)
            self.placeholders['Action']=tf.placeholder(tf.float32, shape=[None,self.getActionSpace()])
            self.placeholders['Reward']=tf.placeholder(tf.float32, shape=[None])
            self.placeholders['Advantage']=tf.placeholder(tf.float32, shape=[None])
            pass
        elif reinforce_type=='A3C':
            #self.agent=A3CAgent()
            pass
        elif reinforce_type=='PPO':
            #self.agent=PPOAgent()
            pass

    def initBuffer(self):
        self.agent.initBuffer(self.batch_size)

    def putBuffer(self, iter, sess, keep_prob):
        return self.agent.putBuffer(self.batch_size, iter, sess, keep_prob)

    def getBuffer(self, valuekey, iter, sess, save_var, keep_prob):
        return self.agent.getBuffer(self.batch_size, valuekey, iter, sess, save_var, keep_prob)

    def getSample(self):
        if self.FLAG_UNITY:
            state=list(self.env.reset().values())[0]
            return np.squeeze(state.visual_observations)
        else:
            return self.env.reset()

    def getActionSpace(self):
        return self.agent.getActionSpace()

    # def runTest(self, sess):
    #     self.agent.runTest(sess)


    

    

        