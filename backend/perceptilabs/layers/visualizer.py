from abc import ABC, abstractmethod


class PerceptiLabsVisualizer(ABC):
    @property
    @abstractmethod
    def visualized_trainables(self):
        """ Returns two tf.Variables (weights, biases) to be visualized in the frontend """
        

