import dill
import pickle

def can_serialize(object_):
    try:
        #return dill.pickles(object_)
        pickle.dumps(object_)
    except:
        return False
    else:
        return True


def serialize(object_):
    return pickle.dumps(object_)


def deserialize(object_):
    return pickle.loads(object_)

