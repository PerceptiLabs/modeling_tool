import os
import pandas as pd


class TypeInferrer:
    IMAGE_TYPES = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

    def __init__(self, max_categories=50, always_allowed=None, never_allowed=None):
        """
        Args:
            max_categories: cannot be categorical type if the number of uniques exceed this number
            always_allowed: list of variables that are always allowed
            never_allowed: list of variables that are never allowed
        """
        self.max_categories = max_categories
        self.always_allowed = always_allowed or list()
        self.never_allowed = never_allowed or list()

    def get_valid_and_default_datatypes(self, series):
        """ Get the datatypes that are valid for this series. Also returns the index of the default one"""
        types_by_priority = {
            'binary': self.is_valid_binary,
            'image': self.is_valid_image,
            'mask': self.is_valid_image,
            'categorical': self.is_valid_categorical,
            'numerical': self.is_valid_numerical,
            'text': self.is_valid_text,
        }

        valid_datatypes = []
        for datatype, is_valid_as_datatype in types_by_priority.items():
            if is_valid_as_datatype(series):
                valid_datatypes.append(datatype)

        for type_ in self.always_allowed:
            if type_ not in valid_datatypes:
                valid_datatypes.append(type_)

        for type_ in self.never_allowed:
            if type_ in valid_datatypes:
                valid_datatypes.remove(type_)

        default_type = valid_datatypes[0]
        valid_datatypes.sort()

        default_index = valid_datatypes.index(default_type)
        return valid_datatypes, default_index

    def get_default_datatype(self, series):
        valid_datatypes, prob_idx = self.get_valid_and_default_datatypes(series)
        if valid_datatypes:
            return valid_datatypes[prob_idx]
        else:
            return None

    def get_valid_and_default_datatypes_for_csv(self, path):
        """ Get the datatypes that are valid for each column in the csv """
        df = pd.read_csv(path)
        return self.get_valid_and_default_datatypes_for_dataframe(df)

    def get_valid_and_default_datatypes_for_dataframe(self, df):
        """ Get the datatypes that are valid for each dataframe

        Arguments:
            df: a pandas dataframe

        Returns:
            a mapping from a column to a tuple: (<list of valid types>, <index of default value>)
        """
        if len(df) == 0:
            raise ValueError("Data is empty!")

        datatypes = {
            name: self.get_valid_and_default_datatypes(series)
            for name, series in df.items()
        }
        return datatypes

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
                return ext.lower() in (x.lower() for x in self.IMAGE_TYPES)
            else:
                return False

        return series.apply(has_image_ext).all()









