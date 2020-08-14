# Overview

Each layer is represented by a LayerSpec. It contains the settings of each layer, replacing the components in the json structure sent from the frontend. The settings are specified as fields with types and default values. These are validated automatically.

The layer spec class solves several problems:

* default values made available _before_ the layer is applied (needed for autosettings)
* inconsistencies can be fixed (e.g., convert "'SAME'" to "SAME")
* trivial changes to the underlying data does not have to affect the entire codebase (i.e., by decoupling the interface from the underlying json structure)


# Adding a new layer

1. Create a new directory with the name of the layer (e.g., 'deeplearningconv')
2. Inside, create 'spec.py'
    1. Implement the abstract LayerSpec class
    2. Add fields corresponding to those of the json network
    3. Implement _from_dict_internal and _to_dict_internal to parse the json network
3. Add 'template.j2' and implement the Jinja template of the layer
4. Add 'imports.json' and add the required import statements
5. Add 'test_integration.py' to ensure that the files work well together (optional, but strongly recommended)
6. Update perceptilabs/layers/definitions.py by adding a LayerMeta matching the new directory.




