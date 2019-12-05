import copy
import tensorflow as tf
import numpy as np

class LayerExtrasReader:
    def __init__(self):
        self.clear()

    def clear(self):
        self._dict = {}

    def to_dict(self):
        return copy.copy(self._dict)

    def _put_in_dict(self, key, value):
        try:
            self._dict[key].update(value)
        except:
            self._dict[key]=value

    def _evalSample(self,sample):
        if isinstance(sample, tf.Tensor) or isinstance(sample, tf.Variable):
            return sample.numpy()
        else:
            return sample

    def set_empty(self, layer_id):
        self._put_in_dict(layer_id,{'Sample': '', 'outShape': '', 'inShape': '', 'Variables': '', 'Default_var':''})
        
    def read(self, session, data_container):
        outShape = ''                
        sample = ''
        inShape=''
        default_var=''
        layer_keys=[]
        if session.layer_id in data_container:
            layer_dict = data_container[session.layer_id]

            if 'Y' in layer_dict:
                Y = layer_dict['Y'] 
                if isinstance(Y, tf.Tensor):
                    outShape = Y.shape.as_list()
                    outShape=outShape[1:]
                else:
                    outShape = np.shape(Y)[1:]
                if not outShape:
                    outShape=[1]
            
            if 'sample' in layer_dict:
                sample = layer_dict['sample']
                default_var = 'sample'
            elif 'Y' in layer_dict:
                sample = layer_dict['Y']
                default_var = 'Y'
            else:
                default_var = layer_dict.keys()[0]
                sample = layer_dict[default_var]
                

            if "X" in layer_dict and "Y" in layer_dict["X"]:
                Xy = layer_dict["X"]["Y"]
                if isinstance(Xy, tf.Tensor):
                    inShape = Xy.shape.as_list()
                    inShape=inShape[1:]
                    if not inShape:
                        inShape=[1]

            layer_keys = list(layer_dict.keys())

            sample=self._evalSample(sample)

        self._put_in_dict(session.layer_id,{'Sample': sample, 'outShape': outShape, 'inShape': str(inShape).replace("'",""), 'Variables': layer_keys, 'Default_var':default_var})
        # print("Session dict:", self.to_dict())
    """
    def read_syntax_error(self, session):
        tbObj=traceback.TracebackException(*sys.exc_info())

        self._put_in_dict(session.layer_id,{"errorMessage": "".join(tbObj.format_exception_only()), "errorRow": tbObj.lineno or "?"})    

    def read_error(self, session, e):
        error_class = e.__class__.__name__
        detail = e
        _, _, tb = sys.exc_info()
        tb_list=traceback.extract_tb(tb)
        line_number=""
        for i in tb_list:
            if i[2]=="<module>":
                line_number=i[1]

        if line_number=="":
            line_number = tb.tb_lineno

        self._put_in_dict(session.layer_id, {"errorMessage": "%s at line %d: %s" % (error_class, line_number, detail), "errorRow": line_number})
    """
