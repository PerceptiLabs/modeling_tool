import os
import pandas as pd


class TypeInferrer:
    IMAGE_TYPES = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

    def __init__(self, max_categories=15):
        """
        Args:
            max_categories: cannot be categorical type if the number of uniques exceed this number
        """
        self.max_categories = max_categories


    def infer_datatypes_from_csv(self, path):
        df = pd.read_csv(path)
        return self.infer_datatypes(df)

    def infer_datatypes(self, df):
        datatypes = {
            name: self.infer_datatype(series)
            for name, series in df.items()
        }
        return datatypes

    def infer_datatype(self, series):
        types_by_priority = {
            'binary': self.is_valid_binary,            
            'image': self.is_valid_image,        
            'categorical': self.is_valid_categorical,
            'numerical': self.is_valid_numerical,            
            'text': self.is_valid_text
        }
        for datatype, is_valid_as_datatype in types_by_priority.items():
            if is_valid_as_datatype(series):
                return datatype

        return None

    def is_valid_text(self, series):
        return series.apply(type).eq(str).all()

    def is_valid_categorical(self, series):
        return series.nunique() <= self.max_categories

    def is_valid_binary(self, series):
        return series.nunique() == 2    
    
    def is_valid_numerical(self, series):
        return (
            series.apply(type).eq(float).all() or
            series.apply(type).eq(int).all()
        )

    def is_valid_image(self, series):
        def has_image_ext(value):
            if isinstance(value, str):
                _, ext = os.path.splitext(value)
                return ext in self.IMAGE_TYPES
            else:
                return False                
        
        return series.apply(has_image_ext).all()

    
    
            
        
        


    
