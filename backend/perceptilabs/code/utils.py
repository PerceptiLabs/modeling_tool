import os
import tempfile

from code.generators import Jinja2CodeGenerator

class RunMacroCodeGenerator(Jinja2CodeGenerator):
    def __init__(self, template, macro, *args, **kwargs):
        self.template = template
        self.macro = macro
        self.args = args
        self.kwargs = kwargs

    def get_code(self):
        all_args = []
        for arg in self.args:
            if isinstance(arg, str):
                arg = '"%s"' % arg
            all_args.append(arg)
            
        for key, value in self.kwargs.items():
            if isinstance(value, str):
                all_args.append('%s="%s"' % (key, value))
            else:
                all_args.append('%s=%s' % (key, value))                
        
        args_str = ', '.join(all_args)
        tmp_template  = '{%'+ 'from "%s" import %s' % (self.template, self.macro) +'%}\n'
        tmp_template += '{{%s(%s)}}' % (self.macro, args_str)
            
        with tempfile.NamedTemporaryFile(mode='w', dir=self.templates_directory) as f:
            f.write(tmp_template)
            f.flush()
            tmp_name = os.path.basename(f.name)
            code = self._render(tmp_name)
        
        return code
