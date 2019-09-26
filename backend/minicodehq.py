def complementString(codeString,layer_type,X):
    if "input_size" in codeString
        input_size=1
        for element in X.get_shape().as_list()[1:]:
            input_size*=element
        input_size=str(input_size)
        codeString=codeString.replace("input_size",input_size)
    
    if "input_shape" in codeString:
        input_shape=str(X.get_shape().as_list())
        codeString=codeString.replace("input_shape",input_shape)

    return codeString