import os
from abc import ABC, abstractmethod

import jinja2
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
        if len(fields) > 0:
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

    def _replace_ckpt_references(self,code):
        import re
        codeString=code
        codeRows=re.split(';|\n',codeString)
        codeRows=list(filter(None,codeRows))
        new_code=""
        for row in codeRows:
            if "loc:@" in row:
                splitRow=row.split("=")
                new_row=splitRow[0]+"=checkpoint['"+ splitRow[1].replace("loc:@","").replace("'","") +"']\n"
                new_code+=new_row
            else:
                new_code+=row+"\n"
        return new_code 

    def replace_ckpt_references(self):
        new_code_parts=[]
        for _codePart in self._code_parts:
            new_code_parts.append(CodePart(name=_codePart.name, code=self._replace_ckpt_references(_codePart.code)))
        self._code_parts=new_code_parts
        

    def get_code(self):    
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
            

class Jinja2CodeGenerator(CodeGenerator):
    TEMPLATES_DIRECTORY = './code/templates/'
    
    def _render(self, path, **kwargs):
        if not hasattr(self, '_jenv'):
            self._jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates_directory),
                                            trim_blocks=True,
                                            lstrip_blocks=True)
            self._jenv.globals.update({
                'zip': zip,
                'len': len,
                'range': range,
                'round̈́': round,
                'None': None,
                'str': str,
                'type': type
            })

            def remove_lspaces(text, count):
                new_text = ''
                lines = text.split('\n')

                for lineno, line in enumerate(lines):
                    last = '\n' if lineno < len(lines) - 1 else ''
                    if line.startswith(' '*count):
                        new_text += line[count:] + last
                    else:
                        new_text += line + last
                return new_text

            self._jenv.filters['remove_lspaces'] = remove_lspaces
                
        code = self._jenv.get_template(path).render(**kwargs)
        return code

    @property
    def templates_directory(self):
        return self.TEMPLATES_DIRECTORY

    
class DataDataCodeGenerator2(Jinja2CodeGenerator):
    def __init__(self, sources, partitions, batch_size, shuffle, seed=0, columns=None, layer_id=None, shuffle_buffer_size=None, lazy=False):
        self._seed = seed
        self.batch_size=batch_size
        self.shuffle=shuffle
        self._layer_id = layer_id
        self.sources=sources
        self.shuffle_buffer_size = shuffle_buffer_size
        self.lazy = lazy

        if columns is not None:
            self.selected_column_indices=[i for i in columns] # convert to ints if necessary.
        else:
            self.selected_column_indices = None
            
        self.partitions = []
        for source, partition in zip(sources, partitions):
            if sum(partition) != 100:
                raise ValueError("Partition percentages do not sum to 100!")

            partition = [partition[0]/100.0, partition[1]/100.0, partition[2]/100.0]
            self.partitions.append(partition)

            if source['type'] == 'directory':
                file_paths = os.listdir(source['path'])
                extensions = [os.path.splitext(p)[1] for p in file_paths]
                
                if len(set(extensions)) != 1:
                    raise ValueError("Can only contain one (and atleast one) type of file!")        
            
                source['ext'] = extensions[0]
            else:
                source['ext'] = os.path.splitext(source['path'])[1]                    

    def get_code(self):
        code = self._render(
            'datadata.j2',
            sources=self.sources,
            shuffle=self.shuffle,
            batch_size=self.batch_size,
            partitions=self.partitions,
            layer_id=self._layer_id,
            selected_columns=self.selected_column_indices,
            seed=self._seed,
            shuffle_buffer_size=self.shuffle_buffer_size,
            lazy=self.lazy
        )
        return code
                     
