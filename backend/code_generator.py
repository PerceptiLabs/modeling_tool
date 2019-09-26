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
    
