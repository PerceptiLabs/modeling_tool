import copy
from abc import ABC, abstractmethod
from collections import namedtuple

CodePart = namedtuple('CodePart', ['name', 'code'])

class CodeGenerator(ABC):
    @abstractmethod
    def get_code(self):
        raise NotImplementedError

    def get_code_parts(self):
        code = self.get_code()        
        code_parts = [CodePart(name=None, code=code)]
        return code_parts

    def __repr__(self):
        text  = "{}\n".format(self.__class__.__name__)
        
        fields = sorted(self.__dict__.items(), key=lambda x: x[0]) # Sort by name
        n_chars = max([len(name) for name, value in fields])
        
        for name, value in fields:
            text += "    {} : {}\n".format(name.ljust(n_chars, " "), value)
            
        return text
    
    
class CustomCodeGenerator(CodeGenerator):
    def __init__(self, input_):
        if isinstance(input_, str):
            self._code_parts = [CodePart(name=None, code=input_)]
        elif isinstance(input_, list) and all([isinstance(x, CodePart) for x in input_]):
            self._code_parts = copy.copy(input_)
        else:
            raise ValueError("Inputs must be either string or list of CodeParts")

    def get_code_parts(self):
        return self._code_parts

    def get_code(self, mode='normal'):    
        code = ''
        for cp in self._code_parts:
            code += cp.code + '\n'            
        return code

    def __repr__(self):
        full_text  = "{}\n".format(self.__class__.__name__)
        full_text += "Code:\n"
        
        for count, line in enumerate(self.get_code().split('\n'), 1):
            full_text += "{} {}".format(count, line)
            
        return full_text
            
