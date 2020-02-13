import dill

def can_serialize(object_):
    try:
        return dill.pickles(object_)
    except:
        return False