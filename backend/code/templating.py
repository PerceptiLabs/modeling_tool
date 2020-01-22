import jinja2
import logging


log = logging.getLogger(__name__)


def log_rendering_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except jinja2.TemplateSyntaxError as e:
            log.error(f"{str(e)} when rendering jinja template. {e.filename}:{e.lineno} '{e.message}'")
            raise
    return wrapper


class J2Engine:
    def __init__(self, templates_directory):
        self._jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_directory),
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

        self._jenv.filters['remove_lspaces'] = self.remove_lspaces
        self._jenv.filters['call_macro'] = self.call_macro

    @staticmethod
    @jinja2.contextfilter
    def call_macro(context, macro_name, *args, **kwargs):
        #import pdb;pdb.set_trace()                
        return context.vars[macro_name](*args, **kwargs)

    @staticmethod
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

    @log_rendering_errors
    def render(self, path, **kwargs):
        text = self._jenv.get_template(path).render(**kwargs)
        return text
    
    @log_rendering_errors        
    def render_string(self, code, **kwargs):
        text = self._jenv.from_string(code).render(**kwargs)
        return text
