import os
import platform

def get_tutorial_data():
    env_var = os.getenv("PL_TUTORIALS_DATA")
    if env_var:
        return env_var

    def ancestors(path):
        cur = os.path.abspath(path)
        parent = os.path.dirname(cur)
        while cur and parent != cur:
            yield parent
            cur = parent
            parent = os.path.dirname(parent)

    # If we're in a wheel, then perceptilabs is next door. Try it.
    for a in ancestors(__file__):
        with_pl = os.path.join(a, "perceptilabs", "tutorial_data")
        if os.path.isdir(with_pl):
            return with_pl

    return None

def get_drives():
    if not platform.system().lower().startswith("win"):
        return None

    import win32api
    drives = win32api.GetLogicalDriveStrings()
    return [d.upper().replace("\\", "") for d in drives.split('\000')[:-1]]

def get_folder_content(full_path):
    if not full_path:
        path = get_tutorial_data()

        if path and os.path.exists(path):
            full_path = path    
        else:
            full_path = os.path.abspath('')

    drives = []
    if full_path == '.' and platform.system() == 'Windows':            
        import win32api
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

    elif not os.path.isdir(full_path):
        return {
            "current_path" : '',
            "dirs" : '',
            "files" :  '',
            "platform": platform.system(),
        }

    if not drives:
        return {
            "current_path" : full_path.replace('\\','/'),
            "dirs" : [x for x in os.listdir(full_path) if os.path.isdir(os.path.join(full_path,x))],
            "files" :  [x for x in os.listdir(full_path) if os.path.isfile(os.path.join(full_path,x))],
            "platform": platform.system(),
        }
    else:
        return {
            "current_path" : full_path.replace('\\','/'),
            "dirs" : drives,
            "files" :  [],
            "platform": platform.system(),
        }


def resolve_dir(path_to_resolve):
    def resolve_windows_path(input_path):
        if '~/Documents' in input_path or "~\\Documents" in input_path:
            # get My Documents regardless of localization
            import ctypes.wintypes

            buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            _ = ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 5, buf)

            return input_path.replace('~/Documents', buf.value)

        elif '~/' in input_path or "~\\" in input_path:
            return os.path.expanduser(input_path)

        else:
            return input_path


    try:
        import platform

        if platform.system() == 'Windows':
            resolved_path = resolve_windows_path(path_to_resolve)
            return os.path.normpath(resolved_path)
        else:
            return os.path.expanduser(path_to_resolve)

    except Exception as e:
        return ''

def get_root_path():
    td = get_tutorial_data()
    if not td:
        return None
    return os.path.dirname(td)
