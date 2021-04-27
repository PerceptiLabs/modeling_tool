import os
import filecmp
import pkg_resources



def get_tutorial_data_directory():
    """ Retrieves the tutorial data directory """
    path = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')
    return path


def get_tutorial_data_files():
    """ Gets the absolute path of every file in the tutorial data directory"""

    root = get_tutorial_data_directory()
    for path, subdirs, files in os.walk(root):
        for name in files:
            full_path = os.path.abspath(os.path.join(path, name))
            yield full_path
            

def is_tutorial_data_file(path):
    """ Checks whether a file path matches the tutorial data directory"""
    path = os.path.abspath(path)
    
    for other in get_tutorial_data_files():
        if os.path.exists(path) and filecmp.cmp(path, other, shallow=True):
            return True        
    return False


    
