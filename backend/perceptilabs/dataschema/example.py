import json
import jsonschema


kernel_started_obj = {
    "time_ingest": "2016-04-06T10:10:19Z",    
    "time_event": "2016-03-06T10:10:09Z",
    "session_id": "123",
    "user_email": "test@test.com",
    "kernel_started": {
        "cpu_count": 456,
        "time_zone": "CET CEST",        
        "memory": {
            "phys_total": 10000,
            "phys_available": 7000,
            "swap_total": 1000,
            "swap_free": 800
        },
        "platform": {
            "platform": "sdas",
            "system": "aa",
            "release": "aaa",
            "version": "bbb",
            "processor": "mmm"
        },
    "python": {
        "version": "1233",
        "packages": ["tensorflow"]
    }
    }
}


training_started_obj = {
    "time_ingest": "2016-04-06T10:10:19Z",    
    "time_event": "2016-03-06T10:10:09Z",
    "session_id": "456",
    "user_email": "test@test.com",
    "training_started": {
        "training_session_id": "1234",
        "graph_spec": {
                "nodes": [
                    {
                        "id": "4567",
                        "name": "datadata_1",                    
                        "type": "layer_datadata",                                        
                        "selected_columns": ['col1', 'col2'],                    
                        "sources_paths": [
                            {
                                "path": "/home/anton/Data/mnist_split/mnist_input.npy",
                                "partition": [70, 20, 10]
                            }
                        ]
                    },
                    {
                        "id": "100",
                        "type": "layer_datadata",                                        
                    }                
                ],
            "edges": [["123", "bb"]]
        },
        "n_parameters": 123
    }
}


training_ended_obj = {
    "time_ingest": "2016-04-06T10:10:19Z",    
    "time_event": "2016-03-06T10:10:09Z",
    "session_id": "456",
    "user_email": "test@test.com",
    "training_ended": {
        "training_session_id": "1234",
        "time_total": 100,
        "time_processing": [1, 1, 2, 1, 2],                
        "graph_spec": {
            "nodes": [
                {
                    "id": "4567",
                    "name": "datadata_1",                    
                    "type": "layer_datadata",                                        
                    "selected_columns": ['col1', 'col2'],                    
                    "sources": [
                        {
                            "path": "/home/anton/Data/mnist_split/mnist_input.npy",
                            "partition": [70, 20, 10]
                        }
                    ]
                }
            ],
            "edges": [["123", "bb"]]
        },
        "num_parameters": 123,
        "memory": {
            "phys_total": 10000,
            "phys_available": [8000, 9000, 7000],
            "swap_total": 1000,
            "swap_free": [800, 700, 300]
        },
        "data_meta": [
            {
                "layer_id": "layer3",
		"training_set_size": 700,
		"validation_set_size": 200,
		"testing_set_size": 100,
		"output_mean": 10.0,
		"output_max": 100.0,
		"output_min": 0.0,
		"output_std": 5.0,
		"output_shape": [28, 28, 3]                
            }
        ]
    }
}

training_started_obj_2 = {
    "training_started": {
        'graph_spec': {
                'edges': [
                    ['1564399781738', '1564399782856'],
                    ['1564399775664', '1564399777283'],
                    ['1564399782856', '1564399790363'],
                    ['1564399786876', '1564399788744'],
                    ['1564399788744', '1564399790363'],
                    ['1564399777283', '1564399781738']
                ],
            'nodes': [
                {'id': '1564399775664', 'type': 'layer_datadata'},
                {'id': '1564399777283', 'type': 'layer_tf1x_reshape'},
                {'id': '1564399788744', 'type': 'layer_tf1x_one_hot'},
                {'id': '1564399781738', 'type': 'layer_tf1x_conv'},
                {'id': '1564399782856', 'type': 'layer_tf1x_fully_connected'},
                {'id': '1564399790363', 'type': 'layer_tf1x_classification'}
            ]
        },
        'n_parameters': 15770,
        'training_session_id': '1234'
    },
    'session_id': '467b092d2eda4d8ab92e314427d59a73',
    'time_event': '2020-04-22T09:21:57.228717',
    'user_email': 'dev@dev.com'
}


with open('master.json', 'r') as f:
    schema = json.load(f)

import os
resolver = jsonschema.RefResolver('file://%s/' % os.path.abspath(os.path.dirname(__file__)), None)

validator = jsonschema.Draft7Validator(schema, resolver=resolver)

#def validate(obj):
#    for e in sorted(validator.iter_errors(obj), key=str):
#        print(e.message)


validator.validate(kernel_started_obj)
validator.validate(training_started_obj)
validator.validate(training_ended_obj)
validator.validate(training_started_obj_2)

