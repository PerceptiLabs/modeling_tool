from abc import abstractmethod
import numpy as np
import os
import pandas as pd
from perceptilabs.utils import get_dataframe_type


class DataFrameResolver:
    @classmethod
    def resolve_dataframe(self, df, dataset_settings):
        dataset_type = get_dataframe_type(dataset_settings)
        if dataset_type == "ObjectDetection":
            return ObjectDetectionDataframeResolver().resolve_dataframe(
                df, dataset_settings
            )
        else:
            return df


class ResolverBaseline:
    @abstractmethod
    def resolve_dataframe(self, df, dataset_settings):
        pass

    def combine_columns(self, df, columns, new_column_name):
        df[new_column_name] = df.apply(
            lambda x: list(str(x[column]) for column in columns), axis=1
        )
        df.drop(columns, inplace=True, axis=1)
        return df

    def combine_rows(self, df, comparing_column, column_to_be_combined):
        df = (
            df.groupby(comparing_column, as_index=False)[column_to_be_combined]
            .agg(list)
            .reindex(columns=df.columns)
        )
        df[column_to_be_combined] = df[column_to_be_combined].apply(
            lambda x: list([item for bbox in x for item in bbox])
        )
        return df


class ObjectDetectionDataframeResolver(ResolverBaseline):
    def resolve_dataframe(cls, df, dataset_settings):
        columns_mapping = cls._get_column_mapping_from_dataset_settings(
            dataset_settings
        )
        df = cls._combine_bounding_box_associated_columns_and_rows(df, columns_mapping)
        return df

    def _get_column_mapping_from_dataset_settings(self, dataset_settings):
        mapping = {}
        for feature_name, feature_dict in dataset_settings["featureSpecs"].items():
            mapping[feature_dict["datatype"].lower()] = feature_name
        return mapping

    def _combine_bounding_box_associated_columns_and_rows(self, df, columns_mapping):
        bounding_box_columns = [
            columns_mapping["category"],
            columns_mapping["x1"],
            columns_mapping["y1"],
            columns_mapping["x2"],
            columns_mapping["y2"],
        ]
        new_column_name = "bounding_box"
        df = self.combine_columns(df, bounding_box_columns, new_column_name)
        image_column = columns_mapping["image"]
        df = self.combine_rows(df, image_column, new_column_name)
        return df
