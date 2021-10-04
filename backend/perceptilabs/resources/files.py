import os


class FileAccess:
    def __init__(self, base_directory=None):
        self._base_directory = base_directory  
    
    def get_local_path(self, file_id):
        file_name = file_id.replace('\\', '/') # TODO: convert the global file ID to a local path

        if self._base_directory and not os.path.isfile(file_name):
            # convert from <file_name> to <base_directory>/<file_name>
            absolute_path = os.path.join(
                self._base_directory, file_name)

            if not os.path.isfile(absolute_path):
                raise ValueError(f"Couldn't find file with id {file_id}")
            
            return absolute_path
        else:
            return file_name

    
