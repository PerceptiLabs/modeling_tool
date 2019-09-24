import numpy as np
from datadata_generator import DataDataCodeGenerator


class dataKeeper():
    def __init__(self, Id, accessProperties, seed=0):
        self.Id = Id
        self.accessProperties = accessProperties
        self.code=None
        self.locals_=None

    def generateCode(self, seed=0):
        sources = self.accessProperties["Sources"]
        partitions = self.accessProperties["Partition_list"]
        batch_size = self.accessProperties["Batch_size"]
        shuffle= self.accessProperties["Shuffle"]
        codeGen = DataDataCodeGenerator(sources, partitions, batch_size, shuffle, seed=seed)
        self.code = codeGen.get_code()
        return self.code

    def executeCode(self, globals_=globals, locals_={}):
        exec(self.code, globals_, locals_)
        self.locals_=locals_
        return locals_

    def updateProperties(self, accessProperties):
        #Remove all sources here which have not been changed from the last accessproperties? We then need a way to send those into the locals and merge with the current ones.
        #Alternative would be to check which variables have changed from last instance (compare code somehow?) and then just put those variables in locals.
        if accessProperties!=self.accessProperties:
            self.accessProperties=accessProperties
            self.generateCode()
            self.executeCode()

    def getMetadata(self):
        if "EnvType" in self.accessProperties:
            return {"Action_space": self.action_space}
        else:
            return {"Dataset_size": self.data_size, "Columns": self.cols}

    @property
    def data_size(self):
        return sum(self.locals_["_data_size"])

    @property
    def output(self):
        return self.locals_["Y"]

    @property
    def sample(self):
        return self.locals_["_sample"][0] if "_sample" in self.locals_ else self.locals_["Y"][0]

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
    import tensorflow as tf
    import numpy as np
    import os
    import skimage
    import json
    import pandas as pd
    Id = 5
    accessProperties = {
        "Columns": [],
        "Dataset_size": 3000,
        "Sources":[{
            "type":"file",
            "path":"C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Data/mnist_split/mnist_input.npy"
        }],
        "Partition_list": [[20, 70, 10]],
        "Batch_size": 10,
        "Shuffle": True
    }
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