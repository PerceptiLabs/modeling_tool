import os
import pkg_resources
import tensorflow as tf

SERVER_PORT = 8181
SCRIPT_FILE = "fastapi_server.py"
REQUIREMENTS_FILE = "fastapi_requirements.txt"
EXAMPLE_JSON_FILE = "example.json"
EXAMPLE_SCRIPT_FILE = "fastapi_example.py"
EXAMPLE_CSV_FILE = "example.csv"
EXAMPLE_REQUIREMENTS_FILE = "fastapi_example_requirements.txt"



STANDARD_LIBRARY_IMPORTS = [
    'from typing import List, Union',
    'import os',
    'import json'
]


THIRD_PARTY_IMPORTS = {
    'pydantic': 'from pydantic import BaseModel, Field, conlist',
    'numpy': 'import numpy as np',    
    'fastapi': 'from fastapi import FastAPI',
    'uvicorn': 'import uvicorn',
    'tensorflow': 'import tensorflow as tf',
}


def _render_imports_snippet():
    code = ""
    for statement in sorted(STANDARD_LIBRARY_IMPORTS):
        code += statement + "\n"

    code += "\n"
    for statement in sorted(THIRD_PARTY_IMPORTS.values()):
        code += statement + "\n"
        
    code += "\n"
    code += "\n"
    code += "MODEL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))\n"
    code += "\n"
    code += "\n"    
    return code 


def _resolve_field(tensor, layer_spec, metadata):
    if layer_spec.datatype == 'categorical':

        if metadata['preprocessing']['dtype'] == str:
            dtype = 'str'
            full_dtype = 'strings'
        elif metadata['preprocessing']['dtype'] == int:
            dtype = 'int'
            full_dtype = 'integers'
        elif metadata['preprocessing']['dtype'] == float:
            dtype = 'float'
            full_dtype = 'floats'            

        descr = f"A list of {full_dtype} with any of the following values: " + ", ".join(
            str(x) for x in metadata['preprocessing']['mapping'].keys())
        
        return f'List[{dtype}]', descr
    elif layer_spec.datatype == 'text':
        return 'List[str]', 'A list of strings'    
    elif layer_spec.datatype == 'numerical':
        return 'List[float]', 'A list of numerical values'
    elif layer_spec.datatype == 'image':

        def make_sample_type(shape):
            if len(shape) == 0:
                return "float"
            else:
                size = shape[0]
                return "conlist_(" + make_sample_type(shape[1:]) + f", size={size})"
            
        sample_shape = tensor.shape.as_list()[1:]        
        type_ = "List[" + make_sample_type(sample_shape) + "]"
        descr = "A matrix of floats with shape [batch_size, " + ", ".join(str(x) for x in sample_shape) + "]"        
        return type_, descr
    else:
        raise NotImplementedError(f"Cannot resolve type string for datatype {layer_spec.datatype}")
    

def _render_data_model_snippet(model, graph_spec, metadata):
    # Create input model

    def render_class_fields(xputs):
        code =  ""
        for feature_name, tensor in xputs.items():
            layer_spec = graph_spec.get_layer_by_feature_name(feature_name)
            type_, description = _resolve_field(
                tensor, layer_spec, metadata[feature_name])
            
            code += f"    {feature_name}: {type_} = \\\n"
            code += f"Field(description='{description}')\n"
        return code

    code  = "with open(os.path.join(MODEL_DIRECTORY, '{}'), 'r') as f:\n".format(EXAMPLE_JSON_FILE)
    code += "    example_data = json.load(f)\n"
    code += "\n"
    code += "\n"
    code += "conlist_ = lambda type_, size: conlist(type_, min_items=size, max_items=size)"
    code += "\n"    
    
    code += "class Inputs(BaseModel):\n"
    code += render_class_fields(model.input)
    code += "    \n"
    code += "    class Config:\n"
    code += "        schema_extra = {'example': example_data}\n"        
    code += "\n"
    code += "\n"

    # Create output model    
    code += "class Outputs(BaseModel):\n"
    code += render_class_fields(model.output)    
    code += "\n"
    code += "\n"    
    return code


def _render_create_app_snippet():
    code  = "def create_app():\n"
    code += "    app = FastAPI(title='PerceptiLabs FastAPI model endpoint', description='This server was generated using [PerceptiLabs](https://www.perceptilabs.com/)')\n"
    code += "    \n"
    code += "    model_directory = os.path.dirname(os.path.realpath(__file__))\n"
    code += "    model = tf.keras.models.load_model(model_directory)\n"
    code += "    \n"
    code += "    @app.get('/healthy')\n"
    code += "    async def healthy():\n"
    code += "        return {'healthy': True}\n"
    code += "    \n"
    code += "    @app.post('/predict', response_model=Outputs)\n"
    code += "    async def predict(inputs: Inputs):\n"
    code += "        x = {\n"
    code += "            name: np.array(raw)\n"
    code += "            for name, raw in inputs.dict().items()\n"
    code += "        } \n"
    code += "        \n"
    code += "        y = model.predict(x)\n"
    code += "        \n"    
    code += "        outputs = Outputs.parse_obj({\n"
    code += "            name: matrix.tolist()\n"
    code += "            for name, matrix in y.items()\n"
    code += "        })\n"
    code += "        return outputs\n"
    code += "    \n"
    code += "    return app\n"
    code += "    \n"
    code += "    \n"    
    return code


def _render_main_snippet(port):
    code  = "OKGREEN = '\033[92m'\n"
    code += "ENDC = '\033[0m'\n"
    code += "\n"
    code += "\n"    
    code += "if __name__ == '__main__':\n"
    code += "    print(OKGREEN + 'HINT:' + ENDC +' go to http://localhost:{port}/docs to interact with the API. Further docs are available at http://localhost:{port}/redoc')\n".format(port=port)
    code += "    app = create_app()\n"
    code += "    \n"        
    code += "    uvicorn.run(app, host='0.0.0.0', port={port})\n".format(port=port)
    code += "\n"
    code += "\n"    
    return code


def render_fastapi_script(path, model, graph_spec, feature_metadata):
    code  = _render_imports_snippet()
    code += _render_data_model_snippet(model, graph_spec, feature_metadata)
    code += _render_create_app_snippet()
    code += _render_main_snippet(SERVER_PORT)

    with open(os.path.join(path, SCRIPT_FILE), 'w') as f:
        f.write(code)


def render_fastapi_requirements(path):
    text = ""
    for module in sorted(THIRD_PARTY_IMPORTS):
        version = pkg_resources.get_distribution(module).version
        text += f"{module}=={version}\n"
        
    with open(os.path.join(path, REQUIREMENTS_FILE), 'w') as f:    
        f.write(text)


def render_fastapi_example_requirements(path):
    third_party_imports = [
        'pandas',
        'pillow',
        'numpy'
    ]
    
    text = ""
    for module in sorted(third_party_imports):
        version = pkg_resources.get_distribution(module).version
        text += f"{module}=={version}\n"
        
    with open(os.path.join(path, EXAMPLE_REQUIREMENTS_FILE), 'w') as f:    
        f.write(text)

        
def render_fastapi_example_script(path, feature_specs):
    def has_image_data():
        return any(spec.datatype == 'image' for spec in feature_specs.values())

    code  = "import json\n"    
    code += "import os\n"
    code += "import requests\n"    
    code += "import pandas as pd\n"            
    code += "from pprint import pprint\n"

    if has_image_data():
        code += "from PIL import Image\n"
        code += "import numpy as np\n"        
        code += "\n"
        code += "\n"                    
        code += "def load_image(path):\n"
        code += "    image = Image.open(path)\n"
        code += "    image = np.array(image, dtype=np.float32)\n"
        code += "    image = np.atleast_3d(image)\n"
        code += "    image = image.tolist()\n"        
        code += "    return image\n"

    code += "\n"                            
    code += "\n"

    code += "def make_payload():\n"
    code += "    model_directory = os.path.dirname(os.path.realpath(__file__))\n"
    code += "    df = pd.read_csv(os.path.join(model_directory, '{}'))\n".format(EXAMPLE_CSV_FILE)
    code += "    \n"
    code += "    data = {\n"

    for name, spec in feature_specs.items():
        if spec.iotype != 'input':
            continue

        if spec.datatype != 'image':
            code += "        '{feature_name}': df['{feature_name}'].tolist(),\n".format(feature_name=name)
        else:
            code += "        '{feature_name}': [load_image(path) for path in df['{feature_name}']],\n".format(feature_name=name)
            
    code += "    }\n"
    code += "    return data\n"    
    code += "\n"                            
    code += "\n"

    code += "if __name__ == '__main__':\n"
    code += "    data = make_payload()\n"
    code += "    response = requests.post('http://localhost:{port}/predict', json=data)\n".format(
        port=SERVER_PORT)
    code += "    pprint(response.json())\n"

    with open(os.path.join(path, EXAMPLE_SCRIPT_FILE), 'w') as f:    
        f.write(code)
