import numpy as np
import copy

import tensorflow as tf
import os
import skimage
import json
import pandas as pd

from code_generator import tensorflow
from codehq import CodeHqNew


class codeHQKeeper():
    def __init__(self, Id, settings):
        self.Id = Id
        self.settings = settings
        self.code=None
        self.locals_=None
        self.hash=None

    def generateCode(self):
        # if self.settings["Code"]=="":
        #     self.code=self.settings["Code"]
        # else:
        codeGen=CodeHqNew.get_code_generator(self.Id, self.settings)
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
        if settings["Code"]:
            layerHash=hash(str(settings["Code"]))
        elif settings["Properties"]:
            layerHash=hash(str(settings["Properties"]))
        else:
            return None

        for hash_ in previousLayerHash:
            if hash_ is None:
                print("Current Layer: ", settings["Name"])
                raise ValueError("The previous layer needs to have been ran to run this layer")
            layerHash+=hash_

        return layerHash


    def updateProperties(self, previousLayerHash, settings, globals_=globals(), locals_={}):
        newHash=self.calculateHash(previousLayerHash, settings)
        if newHash != self.hash and newHash:
            print("Generating new code for the layer ", settings["Name"])
            self.settings=settings
            self.generateCode()
            self.executeCode(globals_=globals_,locals_=locals_)
            self.hash=newHash
    
    @property
    def output(self):
        return self.locals_["Y"]

    @property
    def sample(self):
        return self.locals_["_sample"] if "_sample" in self.locals_ else self.locals_["Y"]