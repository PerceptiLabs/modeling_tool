import pytest
import copy
import pandas as pd
from perceptilabs.data.resolvers.base import ObjectDetectionDataframeResolver


def test_ObjectDetectionDataframeResolver_adds_bounding_box_column():
    df = pd.DataFrame(
        {
            "images": [
                "img1.jpg",
                "img1.jpg",
                "img2.jpg",
                "img2.jpg",
                "img2.jpg",
                "img3.jpg",
            ],
            "categories": ["cat", "dog", "dog", "rat", "cat", "cat"],
            "xmin": [34, 65, 78, 34, 67, 78],
            "xmax": [153, 186, 165, 176, 187, 243],
            "ymin": [21, 67, 89, 156, 76, 54],
            "ymax": [243, 178, 234, 241, 139, 196],
        }
    )

    dataset_settings = {
        "datasetId": "123",
        "randomizedPartitions": True,
        "randomSeed": 789,
        "partitions": [70, 20, 10],
        "featureSpecs": {
            "xmin": {
                "iotype": "Do not use",
                "datatype": "X1",
                "preprocessing": {},
            },
            "xmax": {"iotype": "Do not use", "datatype": "X2", "preprocessing": {}},
            "ymin": {"iotype": "Do not use", "datatype": "Y1", "preprocessing": {}},
            "ymax": {"iotype": "Do not use", "datatype": "Y2", "preprocessing": {}},
            "categories": {
                "iotype": "Do not use",
                "datatype": "category",
                "preprocessing": {},
            },
            "images": {"iotype": "Input", "datatype": "image", "preprocessing": {}},
        },
    }
    processed_df = ObjectDetectionDataframeResolver().resolve_dataframe(
        df, dataset_settings
    )
    assert set(processed_df.columns) == set(["images", "bounding_box"])
    assert processed_df["bounding_box"][0] == [
        "cat",
        "34",
        "21",
        "153",
        "243",
        "dog",
        "65",
        "67",
        "186",
        "178",
    ]
