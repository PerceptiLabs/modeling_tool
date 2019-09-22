import random
from collections import deque
import tensorflow as tf
import numpy as np

class QAgentUnity():
    def __init__(self, env, action_string, safe_dict, workerDict, outputVariables, graph, batch_size):
        memory_size=50000
        self.memory=deque(maxlen=memory_size)
        self.env=env
        self.action_string=action_string
        self.safe_dict=safe_dict
        self.workerDict=workerDict
        self.outputVariables=outputVariables
        self.graph=graph
        self.decay_step=0
        self.put_counter=0
        self.get_counter=0
        self.initBuffer(batch_size)

    def initBuffer(self, batch_size):
        for i in range(batch_size):
            if i == 0:
                # First we need a state
                state=list(self.env.reset().values())[0]

            # Random action (continous) (Assuming the action is between -1 and 1, need to check that later somehow)
            # action = np.random.random(state.previous_vector_actions.shape)*2-1
            
            # Random action (discrete)
            action = random.randrange(state.previous_vector_actions.size)
            action_array=np.zeros(self.getActionSpace())
            action_array[action]=1

            # Get the brain
            next_state = list(self.env.step(action).values())[0]
            
            if state.local_done[0]:               
                # Add experience to memory
                self.remember(np.squeeze(state.visual_observations), action_array, next_state.rewards[0], np.squeeze(next_state.visual_observations), next_state.local_done[0])         
                # Start a new episode
                state=list(self.env.reset().values())[0]
            else:
                # Add experience to memory
                self.remember(np.squeeze(state.visual_observations), action_array, next_state.rewards[0], np.squeeze(next_state.visual_observations), next_state.local_done[0])      
                # Our state is now the next_state
                state = next_state
        self.state=state

    def putBuffer(self, batch_size, iter, sess, keep_prob):
        action = self.getAction(iter, sess, keep_prob)
        next_state, reward, done, state = self.takeStep(action)
        action_array=np.zeros(self.getActionSpace())
        action_array[action]=1
        if type(self.state).__name__=='BrainInfo':
            self.remember(np.squeeze(self.state.visual_observations), action_array, reward, next_state, done)
        else:
            self.remember(self.state, action_array, reward, next_state, done)
        self.state = state
        if done:
            self.env.reset()
        return done

    def getBuffer(self, batch_size, valuekey, iter, sess, save_var, keep_prob):
        if iter==0 and self.get_counter==0:
            self.old_iter=iter
            idx_list=self.randomIdx(batch_size)
            self.memory_batch=[self.memory[idx] for idx in idx_list]
            self.get_counter+=1
        if iter!=self.old_iter:
            idx_list=self.randomIdx(batch_size)
            self.memory_batch=[self.memory[idx] for idx in idx_list]
        
        if valuekey=="Target":
            next_state=[self.memory_batch[i]["Next_state"] for i in range(batch_size)]
            batch=sess.run(self.workerDict['Output'][0], feed_dict = {self.workerDict['Input'][0]: next_state, keep_prob: 1.0})
        else:
            batch=[self.memory_batch[i][valuekey] for i in range(batch_size)]
        self.old_iter=iter
        if save_var and valuekey!="Target":
            value=self.memory[-1][valuekey]
            return np.reshape(value, (1,*np.shape(value)))
        else:
            return batch

    def randomIdx(self, batch_size):
        return list(np.random.choice(np.arange(len(self.memory)),size = batch_size, replace = False))

    def takeStep(self, action):
        next_state=list(self.env.step(int(action)).values())[0]
        return np.squeeze(next_state.visual_observations),next_state.rewards[0],next_state.local_done[0],next_state

    def getAction(self, iter, sess, keep_prob):
        if iter%int(self.action_string['Update_freq'])==0:
            self.copyNetwork(sess)
        self.decay_step+=1
        #exec(self.action_string,{"__builtins__":None},self.safe_dict)
        #return list(self.safe_dict.keys())[-1]
        exp_exp_tradeoff = np.random.rand()
        # An improved version of the epsilon greedy strategy
        explore_probability = float(self.action_string['Eps_min']) + (float(self.action_string['Eps']) - float(self.action_string['Eps_min'])) * np.exp(-float(self.action_string['Eps_decay']) * self.decay_step)
        if (explore_probability < exp_exp_tradeoff):
            return self.randomAction()
        else:
            return self.predictedAction(sess, keep_prob)

    def randomAction(self):
        return random.randrange(self.state.previous_vector_actions.size)

    def predictedAction(self, sess, keep_prob):
        return np.argmax(sess.run(self.workerDict['Output_org'][0], feed_dict = {self.workerDict['Input'][0]: np.reshape(np.squeeze(self.state.visual_observations),(1, *np.shape(np.squeeze(self.state.visual_observations)))), keep_prob: 1.0}))

    def remember(self, state, action, reward, next_state, done):
        self.memory.append({"State":state, "Action":action, "Reward":reward, "Next_state":next_state, "Done":done})

    def getActionSpace(self):
        try:
            return self.state.previous_vector_actions.size
        except:
            return list(self.env.reset().values())[0].previous_vector_actions.size

    def copyNetwork(self, sess):
        update_ops=[]
        for key,value in self.outputVariables.items():
            if key in self.workerDict['Copy_id']:
                if 'W' in value and 'b' in value:
                    update_ops.append(value['W'].assign(self.outputVariables[self.graph[key]['CopyOf']]['W']))
                    update_ops.append(value['b'].assign(self.outputVariables[self.graph[key]['CopyOf']]['b']))
                elif 'W' in value:
                    update_ops.append(value['W'].assign(self.outputVariables[self.graph[key]['CopyOf']]['W']))
        sess.run(update_ops)        



    