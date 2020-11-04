import jinja2
import logging

from perceptilabs.utils import add_line_numbering
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)



def log_rendering_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except jinja2.TemplateSyntaxError as e:
            logger.error(add_line_numbering(e.source))
            logger.error(
                f"{str(e)} when rendering jinja template. "
                f"{e.filename}:{e.lineno} '{e.message}'. "
            )
            raise
    return wrapper


class J2Engine:
    def __init__(self, template_directories, verbose=False):
        self._jenv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_directories),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=jinja2.StrictUndefined
        )
        self._jenv.globals.update({
            'zip': zip,
            'enumerate': enumerate,            
            'len': len,
            'range': range,
            'round̈́': round,
            'None': None,
            'str': str,
            'type': type
        })

        self._jenv.filters['remove_lspaces'] = self.remove_lspaces
        self._jenv.filters['call_macro'] = self.call_macro
        self._jenv.filters['add_spaces'] = self.add_spaces
        self._jenv.filters['remove_spaces'] = self.remove_spaces        
        self._jenv.filters['if_true'] = self.if_true        
        self._verbose = verbose

    @staticmethod
    @jinja2.contextfilter
    def call_macro(context, macro_name, *args, **kwargs):
        #import pdb;pdb.set_trace()                
        return context.vars[macro_name](*args, **kwargs)

    @staticmethod
    def add_spaces(text, count):
        indent = ' '*count
        new_text = ''.join('\n' + indent + line for line in text.splitlines())
        return new_text

    @staticmethod
    def remove_spaces(text, count):
        new_text = ''
        lines = text.split('\n')

        for lineno, line in enumerate(lines):
            last = '\n' if lineno < len(lines) - 1 else ''
            if line.startswith(' '*count):
                new_text += line[count:] + last
            else:
                new_text += line + last
                
        return new_text

    @staticmethod    
    def if_true(text, condition, remove_left_spaces=0):
        if not condition:
            return ''
        
        new_text = ''
        lines = text.split('\n')

        for lineno, line in enumerate(lines):
            last = '\n' if lineno < len(lines) - 1 else ''
            if line.startswith(' '*remove_left_spaces):
                new_text += line[remove_left_spaces:] + last
            else:
                new_text += line + last
                
        return new_text

    @staticmethod
    def remove_lspaces(text, count):
        return J2Engine.remove_spaces(text, count)
    
    @log_rendering_errors
    def render(self, path, **kwargs):
        text = self._jenv.get_template(path).render(**kwargs)

        if self._verbose:
            logger.info(add_line_numbering(text))

        return text
    
    @log_rendering_errors        
    def render_string(self, code, **kwargs):
        text = self._jenv.from_string(code).render(**kwargs)
        
        if self._verbose:
            logger.info(add_line_numbering(text))
        
        return text


if __name__ == "__main__":


    text  = "{% macro hello(x, y) %}\n"
    text += "    {% filter remove_lspaces(8) %}\n"
    text += "        {% if x is not none %}\n"
    text += "            print('hello {{x}}')\n"
    text += "        {% endif %}\n"
    text += "    {% endfilter %}\n"
    text += "    print('bye {{x}}, {{y}}')\n"    
    text += "{% endmacro %}\n"    
    text += "\n"
    text += "{{ hello(x='None', y='bbb')}}\n"

    
    #text  = "{% from 'tf1x_classification.j2' import layer_tf1x_classification %}\n"
    #text += "{{ layer_tf1x_classification(output_layer='_Fully_Connected_1', target_layer='_OneHot_1', #n_epochs='10', loss_function='Quadratic', class_weights='1', optimizer='tf.compat.v1.train.AdamOpti#mizer', learning_rate='0.001', decay_steps='100000', decay_rate='0.96', momentum='0.9', beta1='0.9', beta2='0.999', distributed=False, export_directory=None, layer_name='TrainNormal_Normal_1')}}\n"

    import pkg_resources
    from perceptilabs.utils import add_line_numbering
    from perceptilabs.core_new.layers.templates import J2Engine
    from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE, TEMPLATES_DIRECTORY

    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
    engine = J2Engine(templates_directory)

    code = engine.render_string(text)

    print(add_line_numbering(code))
    
    # import pdb; pdb.set_trace()
    
