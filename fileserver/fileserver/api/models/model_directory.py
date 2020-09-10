import os

def get_contents(root):
    if not os.path.exists(root):
        return None

    if not os.path.isdir(root):
        raise ValueError(f"{root} isn't a directory")

    # expand the tuples from os.walk and then join the dir with the filename to make a flat list
    paths = [f"{d}/{f}" for d, _, files in os.walk(root) for f in files]

    return [{"path": p, "size": os.path.getsize(p)} for p in paths]
