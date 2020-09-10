import os
import platform

def get_drives(requested_path):
    if requested_path != '/' or not platform.system().lower().startswith("win"):
        return None

    import win32api
    drives = win32api.GetLogicalDriveStrings()
    return drives.split('\000')[:-1]

def get_folder_content(requested_path):
    if not os.path.exists(requested_path):
        return None

    if not os.path.isdir(requested_path):
        raise ValueError(f"{requested_path} isn't a directory")

    drives = get_drives(requested_path)
    if not drives:
        return {
            "current_path" : requested_path.replace('\\','/'),
            "dirs" : [x for x in os.listdir(requested_path) if os.path.isdir(os.path.join(requested_path,x))],
            "files" :  [x for x in os.listdir(requested_path) if os.path.isfile(os.path.join(requested_path,x))],
            "platform": platform.system(),
        }
    else:
        return {
            "current_path" : requested_path.replace('\\','/'),
            "dirs" : drives,
            "files" :  [],
            "platform": platform.system(),
        }
