import random
from collections import deque
import tensorflow as tf
import numpy as np

import logging
log = logging.getLogger(__name__)


class QAgent():
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
        self.meanings = env.unwrapped.get_action_meanings()
        self.pred=np.zeros(self.getActionSpace())        
        self.initBuffer(batch_size)


    def initBuffer(self, batch_size):
        for i in range(batch_size):
            if i == 0:
                # First we need a state
                state=self.env.reset()
            # Random action
            action = random.randrange(self.env.action_space.n)
            # Get the rewards
            next_state, reward, done, _ = self.takeStep(action)
            action_array=np.zeros(self.getActionSpace())
            action_array[action]=1
            
            if done:               
                # Add experience to memory
                self.remember(state, action_array, reward, next_state, done)         
                # Start a new episode
                state=self.env.reset()                
            else:
                # Add experience to memory
                self.remember(state, action_array, reward, next_state, done)      
                # Our state is now the next_state
                state = next_state
        self.state=state
                

    def putBuffer(self, batch_size, iter, sess, keep_prob):
        action = self.getAction(iter, sess, keep_prob)
        next_state, reward, done, _ = self.takeStep(action)
        action_array=np.zeros(self.getActionSpace())
        action_array[action]=1
        self.remember(self.state, action_array, reward, next_state, done)
        self.state = next_state
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
        return self.env.step(action)

    def getAction(self, iter, sess, keep_prob):
        if iter%int(self.action_string['Update_freq'])==0:
            self.copyNetwork(sess)
        self.decay_step+=1
        #exec(self.action_string,{"__builtins__":None},self.safe_dict)
        #return list(self.safe_dict.keys())[-1]
        exp_exp_tradeoff = np.random.rand()
        # An improved version of the epsilon greedy strategy

        #self.action_string['Eps_min'] = 1.0
        
        explore_probability = float(self.action_string['Eps_min']) + (float(self.action_string['Eps']) - float(self.action_string['Eps_min'])) * np.exp(-float(self.action_string['Eps_decay']) * self.decay_step)
        log.info("qagent has explore_probability: {}".format(explore_probability))                    
        if exp_exp_tradeoff < explore_probability:
            action = self.randomAction()
            log.info("qagent selected action {} ({}) at random".format(action, self.meanings[action]))            
        else:
            action = self.predictedAction(sess, keep_prob)            
            log.info("qagent selected action {} ({}) by prediction".format(action, self.meanings[action]))
        return action

    def randomAction(self):
        return random.randrange(self.env.action_space.n)

    def predictedAction(self, sess, keep_prob):
        feed_dict = {self.workerDict['Input'][0]: self.state.reshape((1, *self.state.shape)),
                     keep_prob: 1.0}

        pred = sess.run(self.workerDict['Output_org'][0], feed_dict=feed_dict)
        self.pred = pred

        log.debug("qagent predicted {}".format(pred))                                
        return np.argmax(pred)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append({"State":state, "Action":action, "Reward":reward, "Next_state":next_state, "Done":done})

    def getActionSpace(self):
        return self.env.action_space.n

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




    
