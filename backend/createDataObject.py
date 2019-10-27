import numpy as np
import itertools


def RGB2RGBa(data):
    data=np.squeeze(data)
    (w,h,d)=np.shape(data)
    newData=np.empty((w, h, 4))
    normalizedData=np.around((data/data.max(0).max(0))*255)
    newData[:, :, 0:3] = normalizedData
    newData[:,:,3]=255
    flatData=np.reshape(newData,-1)
    return flatData


def grayscale2RGBA(data):
    data=np.squeeze(data)
    (w,h)=np.shape(data)
    newData=np.empty((w, h, 4))
        
    if data.max()!=0:
        normalizedData=np.around((data/data.max())*255)
    else:
        normalizedData=data
    newData[:, :, 0] = normalizedData
    newData[:, :, 1] = newData[:, :, 2] = newData[:, :, 0]
    newData[:,:,3]=255
    flatData=np.reshape(newData,-1)

    return flatData

def subsample(sample,endSize=500):
    if len(sample.shape)==1:
        length=sample.size
        if length>endSize:
            lenRatio=length/endSize
        else:
            lenRatio=1
        result=sample[::int(lenRatio)]

    elif len(sample.shape)>=2:
        height,width=sample.shape[0:2]
        if height>endSize or width>endSize:
            if height>width:
                heightRatio=widthRatio=height/endSize
            else:
                heightRatio=widthRatio=width/endSize
        else:
            heightRatio=widthRatio=1
        result=sample[::int(np.ceil(heightRatio)),::int(np.ceil(widthRatio))]
    else:
        result=sample

    return result


def convertToList(npy):
    if np.any(npy.ravel()==None):
        return None    
    npy = np.atleast_1d(npy).tolist()
    return npy
    
    '''
    if isinstance(npy, list):
        return npy
    
    if len(npy.shape)==0:
        import pdb; pdb.set_trace()
        if isinstance(npy, np.integer):
            npy=[int(npy)]
        elif isinstance(npy, np.floating):
            npy=[float(npy)]
    elif len(npy.shape)==1:
        npy=npy.tolist()
    elif len(npy.shape)>1:
        npy=npy.tolist()
    return npy
    '''

TYPE_BAR       = "bar"
TYPE_LINE      = "line"
TYPE_GRAYSCALE = "grayscale"
TYPE_RGBA      = "rgba"
TYPE_HEATMAP   = "heatmap"
TYPE_SCATTER   = "scatter"
TYPE_PIE       = "pie"

BAR_LINE_THRESHOLD = 25

def bar(dataVec, subSampleSize=None):
    obj = {"data": convertToList(dataVec)}
    return obj


def line(dataVec, subSampleSize=None):
    obj = {"data": convertToList(dataVec)}
    return obj


def heatmap(dataVec, subSampleSize=None):
    data = subsample(dataVec, subSampleSize)
    data = convertToList(data)
    
    new_data = []
    for i in range(len(data)):
        for j in range(len(data[0])):
            new_point = [i, j, data[i][j]]
            new_data.append(new_point)
            
    obj = {"data": new_data}
    return obj


def grayscale(dataVec, subSampleSize=None):
    height, width = dataVec.shape[0:2]
    dataVec = grayscale2RGBA(dataVec)
    
    output = {"data": convertToList(dataVec),
              "type": TYPE_RGBA,
              "height": height,
              "width": width}
    return output


def rgb(dataVec, subSampleSize=None):
    height, width = dataVec.shape[0:2]
    dataVec = RGB2RGBa(dataVec)
    
    output = {"data": convertToList(dataVec),
              "type": TYPE_RGBA,
              "height": height,
              "width": width}
    return output


def scatter(dataVec, subSampleSize=None):
    obj = {"data": convertToList(dataVec)}
    return obj    


def pie(dataVec, subSampleSize=None):
    try:
        list_ = [dict(name=n, value=float(v)) for n, v in dataVec]
    except Exception as e:
        print(e)
        print(dataVec)
        raise
    output = {"data": list_}
    return output

TYPE_TO_SPEC_FUNC = {TYPE_BAR: bar,
                     TYPE_LINE: line,
                     TYPE_GRAYSCALE: grayscale,
                     TYPE_RGBA: rgb,
                     TYPE_HEATMAP: heatmap,
                     TYPE_SCATTER: scatter,
                     TYPE_PIE: pie}

def getType(dataVec):
    dataVec = np.asarray(dataVec)
    
    type_ = None
    shape = dataVec.shape
    dims = len(shape)

    if dims == 1 and shape[0] < BAR_LINE_THRESHOLD:
        return TYPE_BAR
    elif dims == 1 and shape[0] >= BAR_LINE_THRESHOLD:
        return TYPE_LINE
    elif dims == 2:
        return TYPE_GRAYSCALE
    elif dims == 3 and shape[-1] == 1:
        return TYPE_GRAYSCALE        
    elif dims == 3 and shape[-1] == 3:
        return TYPE_RGBA
    elif dims == 3:
        return TYPE_HEATMAP        
    else:
        return TYPE_BAR        

    return type_

def createDataObject(dataList,typeList=None,styleList=None,nameList=None,subSampleSize=500):
    # return {}
    if np.any(np.asarray(dataList).ravel() is None):
        return {}
    if not typeList: # default-argument-lists tend to misbehave
        typeList = []
    if not styleList:
        styleList = []
    if not nameList:
        nameList = []    

    dataList = [np.asarray(vec) for vec in dataList] # if not array, convert
    
    size = max(map(np.size, dataList)) # used to make sure all arrays are equal length
    if size > 1:
        dataList = [vec[0:size] for vec in dataList] 
    
    # Assert that each data vector has a type.
    for i in range(len(typeList), len(dataList)):
        type_ = getType(dataList[i])
        typeList.append(type_)

    seriesList = []
    for dataVec, type_, style, name in itertools.zip_longest(dataList, typeList,
                                                             styleList, nameList):

        if dataVec is None:
            break

        customFieldsFunc = TYPE_TO_SPEC_FUNC.get(type_)
        if customFieldsFunc is None:
            raise ValueError("Unknown type: " + type_)        

        seriesEntry = dict(type=type_)
        if name:
            seriesEntry['name'] = name
        if style:
            seriesEntry['linestyle'] = style
            
        seriesEntry.update(customFieldsFunc(dataVec, subSampleSize))        
        seriesList.append(seriesEntry)

    dataObject = dict()
    dataObject["xLength"] = dataList[0].size
    dataObject["series"]  = seriesList    
    if nameList:
        dataObject["legend"] = {"data": [n for n in nameList]}        
    return dataObject
                  
        



if __name__ == "__main__":
    a=createDataObject([1])
    b=createDataObject([np.asarray([[1,2], [3,4]])])
    X = np.zeros((24, 24))    
    bb=createDataObject([X])
    
    X = np.zeros((3, 3, 2))
    cc=createDataObject([X])

    
    import pdb; pdb.set_trace()



    
    

    
    
    
    
    
