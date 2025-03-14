import numpy as np
import itertools

DEFAULT_IMAGE_SUBSAMPLE_SIZE = 100
DEFAULT_SUBSAMPLE_SIZE = 200
DEFAULT_SUBSAMPLE_RATIO = 1
BAR_LINE_THRESHOLD = 25

MAX_DATA_POINTS = 1000000
MIN_IMAGE_SIZE = 10
MAX_IMAGE_SIZE = 2000
MIN_1D_SIZE = 1000

TYPE_BAR = "bar"
TYPE_BAR_D = "bar_detailed"
TYPE_LINE = "line"
TYPE_GRAYSCALE = "grayscale"
TYPE_RGBA = "rgba"
TYPE_HEATMAP = "heatmap"
TYPE_SCATTER = "scatter"
TYPE_PIE = "pie"
TYPE_MASK = "mask"


def needs_compression(image: np.ndarray) -> bool:
    if image.shape[0] >= MAX_IMAGE_SIZE or image.shape[1] >= MAX_IMAGE_SIZE:
        return True
    else:
        return False


def normalization(image, from_min, from_max, to_min, to_max):

    from_range = from_max - from_min
    to_range = to_max - to_min
    scaled = np.array((image - from_min) / float(from_range), dtype=float)
    return to_min + (scaled * to_range)


def RGB2RGBa(data: np.ndarray, normalize: bool):
    """Converts RGB to RGBa"""
    data = np.squeeze(data)
    (w, h, d) = np.shape(data)
    newData = np.empty((w, h, 4))

    if normalize:
        normalizedData = np.around((data / data.max(0).max(0)) * 255)
        newData[:, :, 0:3] = normalizedData
    else:
        # De-Normalize because we normalized during preprocessing
        denormalizedData = normalization(data, 0.0, 1.0, 0, 255)
        newData[:, :, 0:3] = denormalizedData

    newData[:, :, 3] = 255

    flatData = np.reshape(newData, -1)

    return flatData


def grayscale2RGBA(data: np.ndarray):
    """Converts grayscale to RGBA"""
    # method accepts only 2 dimensional arrays or 3 dimensional arrays with final dimension = 1.
    if len(np.shape(data)) > 2:
        data = np.squeeze(data, axis=2)

    (w, h) = np.shape(data)
    newData = np.empty((w, h, 4))

    if data.max() != 0:
        normalizedData = np.around((data / data.max()) * 255)
    else:
        normalizedData = data
    newData[:, :, 0] = normalizedData
    newData[:, :, 1] = newData[:, :, 2] = newData[:, :, 0]
    newData[:, :, 3] = 255
    flatData = np.reshape(newData, -1)

    return flatData


def subsample(sample: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples a n-dimensional array according to ratio

    Args:
        sample (np.ndarray): Preview sample
        ratio (int): Ratio to subsample

    Return:
        x_data (list): Data of x-coordinates
        y_data (np.ndarray): Data of y-coordinates
    """
    x_data = None
    y_data = None

    if len(sample.shape) == 1:
        length = sample.size

        if length < MIN_1D_SIZE:
            ratio = 1

        x_data = [i for i in range(0, length, int(ratio))]
        y_data = sample[:: int(ratio)]

    elif len(sample.shape) >= 2:
        height, width = sample.shape[0:2]

        if height < MIN_IMAGE_SIZE or width < MIN_IMAGE_SIZE:
            y_data = sample
        else:
            y_data = sample[:: int(np.ceil(ratio)), :: int(np.ceil(ratio))]

    else:
        y_data = sample

    return x_data, y_data


def convertToList(npy: np.ndarray):
    """Converts an np.ndarray into a list"""
    if np.any(npy.ravel() == None):
        return ""

    npy = np.atleast_1d(npy).tolist()
    return npy


def bar(data_vec: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples n-dimensional array into bar format"""
    x_data, y_data = subsample(data_vec, ratio)
    data = convertToList(y_data)

    obj = {"x_data": x_data, "data": data}
    return obj


def bar_detailed(
    data_vec: np.ndarray, name_list: list = None, ratio: int = DEFAULT_SUBSAMPLE_RATIO
):
    """Subsamples n-dimensional array into bar format"""
    _, y_data = subsample(data_vec, ratio)
    x_data = list(range(len(y_data)))
    data = convertToList(y_data)
    series_data = list()
    # Gets indiviudal bar stacks and appends them to a list
    for i in range(len(data)):
        if name_list is not None and len(name_list) > 0:
            series_data.append(
                {
                    "name": name_list[i],
                    "type": "bar",
                    "stack": "total",
                    "label": {"show": False},
                    "emphasis": {"focus": "series"},
                    "data": data[i],
                }
            )
        else:
            series_data.append(
                {
                    "name": str(i),
                    "type": "bar",
                    "stack": "total",
                    "label": {"show": False},
                    "emphasis": {"focus": "series"},
                    "data": data[i],
                }
            )

    if name_list is not None and len(name_list) > 0:
        x_data = name_list

    obj = {"x_data": x_data, "data": series_data}

    return obj


def line(data_vec: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples n-dimensional array into line format"""
    x_data, y_data = subsample(data_vec, ratio)
    data = convertToList(y_data)
    obj = {"x_data": x_data, "data": data}
    return obj


def heatmap(
    data_vec: np.ndarray,
    name_list: list = [],
    ratio: int = DEFAULT_SUBSAMPLE_RATIO,
    **kwargs
):
    """Subsamples n-dimensional array into heatmap format"""
    x_data, y_data = subsample(data_vec, ratio)
    data = convertToList(y_data)
    show_data = kwargs.get("show_data", False)
    new_data = []
    for i in range(len(data)):
        for j in range(len(data[0])):
            new_point = [i, j, data[i][j]]
            new_data.append(new_point)
    x_axis = {
        "type": "category",
        "name": "Prediction",
        "data": name_list,
        "splitArea": {"show": True},
    }
    y_axis = {
        "type": "category",
        "name": "Actual",
        "data": name_list,
        "splitArea": {"show": True},
    }

    series = [
        {"name": "", "type": "heatmap", "data": new_data, "label": {"show": show_data}}
    ]

    obj = {"series": series, "x_axis": x_axis, "y_axis": y_axis}
    return obj


def grayscale(data_vec: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples n-dimensional array into greyscale format"""
    x_data, y_data = subsample(data_vec, ratio)
    height, width = y_data.shape[0:2]
    data = grayscale2RGBA(y_data)

    obj = {
        "x_data": x_data,
        "data": convertToList(data),
        "type": TYPE_RGBA,
        "height": height,
        "width": width,
    }

    return obj


def rgb(data_vec: np.ndarray, normalize: bool, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples n-dimensional array into RGB format"""
    if needs_compression(data_vec) and ratio == 1:
        ratio *= 2

    x_data, y_data = subsample(data_vec, ratio)
    height, width = y_data.shape[0:2]
    y_data = RGB2RGBa(y_data, normalize)
    obj = {
        "x_data": x_data,
        "data": convertToList(y_data),
        "type": TYPE_RGBA,
        "height": height,
        "width": width,
    }

    return obj


def scatter(data_vec: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    """Subsamples n-dimensional array into scatter format"""
    x_data, y_data = subsample(data_vec, ratio)
    data = convertToList(y_data)

    obj = {"x_data": x_data, "data": data}
    return obj


def pie(data_vec: np.ndarray):
    """Subsamples n-dimensional array into pie format"""
    try:
        list_ = [dict(name=n, value=float(v)) for n, v in data_vec]
    except Exception as e:
        raise
    output = {"data": list_}
    return output


def mask(data_vec: np.ndarray, ratio: int = DEFAULT_SUBSAMPLE_RATIO):
    # TODO(mukund): generate color images instead of greyscale
    if len(data_vec.shape) == 3:
        data_vec = np.argmax(data_vec, axis=2)  # getting class values
    return grayscale(data_vec, ratio)


def getType(data_vec: np.ndarray, type_: str = None):
    """Given an n-dimensional array, find its type"""
    data_vec = np.asarray(data_vec)

    shape = data_vec.shape
    dims = len(shape)

    if type_ == "bar_detailed":
        return TYPE_BAR_D

    if type_ == "mask":
        return TYPE_MASK

    if dims == 0:
        if data_vec == 0:
            return TYPE_SCATTER
        else:
            return TYPE_BAR
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
        return TYPE_SCATTER


def create_type_object(
    data_vec: np.ndarray,
    type_: str,
    name_list: list,
    normalize: bool = True,
    subsample_ratio: int = DEFAULT_SUBSAMPLE_RATIO,
    **kwargs
):
    """Create data object based on type

    Args:
        data_vec (np.ndarray): N-dimensional array
        type_ (str): Type to create
        normalize (bool): State to normalize data
        subsample_ratio (int): Ratio to subsample the n-dimensional array

    Returns:
        type_object (dict): Dictionary containing object information
    """
    type_object = None

    if type_ == TYPE_BAR:
        type_object = bar(data_vec, ratio=subsample_ratio)
    elif type_ == TYPE_BAR_D:
        type_object = bar_detailed(data_vec, name_list, ratio=subsample_ratio)
    elif type_ == TYPE_LINE:
        type_object = line(data_vec, ratio=subsample_ratio)
    elif type_ == TYPE_RGBA:
        type_object = rgb(data_vec, normalize, ratio=subsample_ratio)
    elif type_ == TYPE_GRAYSCALE:
        type_object = grayscale(data_vec, ratio=subsample_ratio)
    elif type_ == TYPE_HEATMAP:
        type_object = heatmap(data_vec, name_list, ratio=subsample_ratio, **kwargs)
    elif type_ == TYPE_SCATTER:
        type_object = scatter(data_vec, ratio=subsample_ratio)
    elif type_ == TYPE_PIE:
        type_object = pie(data_vec)
    elif type_ == TYPE_MASK:
        type_object = mask(data_vec, ratio=subsample_ratio)
    else:
        raise ValueError("Unknown type: " + type_)

    return type_object


def create_data_object(
    data_list: list,
    type_list: list = None,
    style_list: list = None,
    name_list: list = None,
    normalize: bool = True,
    subsample_ratio: int = DEFAULT_SUBSAMPLE_RATIO,
    **kwargs
):
    """Create a data object to be utilized by frontend. If applicable, normalize and
       subsample the incoming n-dimensional array

    Args:
        data_list (list): List of n-dimensional arrays
        type_list (list): List of types of previews
        style_list (list): List of styles to display
        name_list (list): List of names of n-dimensional arrays
        normalize (bool): State to normalize data
        subsample_ratio (int): Ratio to subsample the n-dimensional arrays

    Returns:
        data_object (dict): Dictionary describing the n-dimensional arrays
    """
    if np.any(np.asarray(data_list).ravel() is None):
        return {}
    if type_list is None:
        type_list = list()
    if style_list is None:
        style_list = list()
    if name_list is None:
        name_list = list()

    data_list = [np.asarray(vec) for vec in data_list]  # if not array, convert
    try:
        size = max(map(np.size, data_list))
    except:
        size = 0
        # used to make sure all arrays are equal length
    series_list = []

    if size > 1:
        data_list = [vec[0:size] for vec in data_list]

    type_list_new = type_list
    # Assert that each data vector has a type.
    for i in range(len(type_list), len(data_list)):
        if "bar_detailed" in type_list:
            type_ = getType(data_list[i], "bar_detailed")
        elif "mask" in type_list:
            type_ = getType(data_list[i], "mask")
        else:
            type_ = getType(data_list[i])
        type_list_new.append(type_)

    for data_vec, type_, style, name in itertools.zip_longest(
        data_list, type_list_new, style_list, name_list
    ):
        if data_vec is None:
            break

        type_object = create_type_object(
            data_vec, type_, name_list, normalize, subsample_ratio, **kwargs
        )
        series_entry = dict(type=type_)

        if name:
            series_entry["name"] = name

        if style:
            series_entry["linestyle"] = style

        series_entry.update(type_object)
        series_list.append(series_entry)

    data_object = dict()

    if size > 0:
        if "bar_detailed" in type_list:
            data_object["xLength"] = len(data_list[0])
            data_object["series"] = type_object["data"]
            data_object["nameList"] = name_list
        elif "heatmap" in type_list:
            data_object["series"] = type_object["series"]
            data_object["x_axis"] = type_object["x_axis"]
            data_object["y_axis"] = type_object["y_axis"]
        else:
            data_object["xLength"] = data_list[0].size
            data_object["series"] = series_list

            if name_list:
                data_object["legend"] = {"data": [n for n in name_list]}

    return data_object


def createDataObject(
    data_list: list,
    type_list: list = None,
    style_list: list = None,
    name_list: list = None,
    normalize: bool = True,
    subsample_ratio: int = DEFAULT_SUBSAMPLE_RATIO,
    **kwargs
):
    """Backwards compatibility alias for create_data_object. Don't use!"""
    return create_data_object(
        data_list=data_list,
        type_list=type_list,
        style_list=style_list,
        name_list=name_list,
        normalize=normalize,
        subsample_ratio=subsample_ratio,
        **kwargs
    )


if __name__ == "__main__":
    a = createDataObject([1])
    b = createDataObject([np.asarray([[1, 2], [3, 4]])])
    X = np.zeros((24, 24))
    bb = createDataObject([X])

    X = np.zeros((3, 3, 2))
    cc = createDataObject([X])

    import pdb

    pdb.set_trace()
