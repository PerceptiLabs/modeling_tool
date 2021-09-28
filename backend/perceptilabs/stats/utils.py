from perceptilabs.createDataObject import createDataObject


def return_on_failure(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception as e:
                print(e)
                return value
        return applicator
    return decorate


def create_data_object_for_list_of_1D_arrays(values, object_name, name_list=None):
    num_lists = len(values)
    dataObj = createDataObject(
            values,
            type_list=num_lists*['line'],
            name_list=name_list,
            style_list=[{"color":"#83c1ff"},
                        {"color":"#0070d6"},
                        {"color":"#6b8ff7"}]
                        )
    obj = {object_name: dataObj}
    return obj