import numpy as np
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

    def generateCode(self, seed=0):
        if self.accessProperties["Code"]=="":
            self.code=self.accessProperties["Code"]
        else:
            if self.accessProperties["Type"]=="Fully_Connected":
                codeGen=fc_generator()
            elif ...

            
            self.code = codeGen.get_code()
        return self.code

    def executeCode(self, globals_=globals(), locals_={}):
        globals_=copy.copy(globals_)
        locals_=copy.copy(locals_)
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
    
    @property
    def output(self):
        return self.locals_["Y"]

    @property
    def sample(self):
        return self.locals_["_sample"] if "_sample" in self.locals_ else self.locals_["Y"]