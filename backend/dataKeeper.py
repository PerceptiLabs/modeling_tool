import numpy as np
from code_generator import DataDataCodeGenerator
import copy

import tensorflow as tf
import os
import skimage
import json
import pandas as pd


class dataKeeper():
    def __init__(self, Id, accessProperties, seed=0):
        self.Id = Id
        self.accessProperties = accessProperties
        self.code=None
        self.locals_=None
        self.hash=None

    def generateCode(self, seed=0):
        sources = self.accessProperties["Sources"]
        partitions = self.accessProperties["Partition_list"]
        batch_size = self.accessProperties["Batch_size"]
        shuffle= self.accessProperties["Shuffle_data"]
        columns = self.accessProperties["Columns"] if "Columns" in self.accessProperties else []
        codeGen = DataDataCodeGenerator(sources, partitions, batch_size, shuffle, seed=seed, columns=columns)
        self.code = codeGen.get_code()
        return self.code

    def executeCode(self, globals_=globals(), locals_={}):
        globals_=copy.copy(globals_)
        locals_=copy.copy(locals_)
        exec(self.code, globals_, locals_)
        self.locals_=locals_
        return locals_

    def calculateHash(self, previousLayerHash, settings):
        """
            previousLayerHash should be a list
        """
        if "Code" in settings and settings["Code"]:
            layerHash=hash(str(settings["Code"]))
        else:
            layerHash=hash(str(settings))

        for hash_ in previousLayerHash:
            if hash_ is None:
                raise ValueError("The previous layer needs to have been ran to run this layer")
            layerHash+=hash_

        return layerHash


    def updateProperties(self, previousLayerHash, settings, globals_=globals(), locals_={}):
        newHash=self.calculateHash(previousLayerHash, settings)
        if newHash != self.hash:
            print("Generating new code for the layer ", settings["Name"])
            self.settings=settings
            self.generateCode()
            self.executeCode(globals_=globals_,locals_=locals_)
            self.hash=newHash

    def getMetadata(self):
        if "EnvType" in self.accessProperties:
            return {"Action_space": self.action_space}
        else:
            return {"Dataset_size": int(self.data_size), "Columns": int(self.cols)}

    @property
    def batch_size(self):
        return self.locals_["_batch_size"]

    @property
    def trainingIterations(self):
        return int(self.locals_["X_train_size"]/int(self.batch_size))

    @property
    def maxIter(self):
        return int((self.locals_["X_train_size"]+self.locals_["X_validation_size"])/int(self.batch_size))

    @property
    def maxTestIter(self):
        return self.locals_["X_test_size"]

    @property
    def train_iterator(self):
        return self.locals_["train_iterator"]

    @property
    def validation_iterator(self):
        return self.locals_["validation_iterator"]

    @property
    def test_iterator(self):
        return self.locals_["test_iterator"]

    @property
    def data_size(self):
        return sum(self.locals_["_data_size"])

    @property
    def output(self):
        return self.locals_["Y"]

    @property
    def sample(self):
        return self.locals_["_sample"] if "_sample" in self.locals_ else self.locals_["Y"][0]

    @property
    def cols(self):
        try:
            return self.locals_["cols"]
        except:
            return 0

    @property
    def partition_summary(self):
        return self.locals_["_partition_summary"]


if __name__ == "__main__":
    
    Id = 5
    accessProperties = {'Batch_size': 10,
                            'Category': 'Local',
                            'Columns': [0,1,2],
                            'Content': '',
                            'Dataset_size': 3000,
                            'Partition_list': [[70,
                                                20,
                                                10]],
                            'Shuffle_data': True,
                            'Sources': [{'path': 'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication.csv',
                                        'type': 'file'}],
                            'Type': 'Data',
                            'errorMessage': "'NoneType' "
                                            'object '
                                            'is '
                                            'not '
                                            'subscriptable'}
    dk=dataKeeper(Id,accessProperties)
    code=dk.generateCode()
    print(code)
    globals_ = {'tf': tf,
                    'os': os,
                    'skimage': skimage,
                    'pd': pd,
                    'json': json,                  
                    'np': np}
    safe_dict=dk.executeCode(globals_=globals_)
    print(safe_dict)

    print(dk.partition_summary)
    print(dk.cols)
    print(dk.sample)