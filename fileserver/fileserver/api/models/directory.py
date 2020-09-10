import os
import platform

def get_tutorial_data():
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

def get_folder_content(requested_path):
    def get_drives(requested_path):
        if requested_path != '/' or not platform.system().lower().startswith("win"):
            return None

        import win32api
        drives = win32api.GetLogicalDriveStrings()
        return drives.split('\000')[:-1]

    abs_path = os.path.abspath(requested_path)
    if not os.path.exists(abs_path):
        return None

    if not os.path.isdir(abs_path):
        raise ValueError(f"{requested_path} isn't a directory")

    drives = get_drives(abs_path)
    if not drives:
        return {
            "current_path" : abs_path.replace('\\','/'),
            "dirs" : [x for x in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path,x))],
            "files" :  [x for x in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path,x))],
            "platform": platform.system(),
        }
    else:
        return {
            "current_path" : abs_path.replace('\\','/'),
            "dirs" : drives,
            "files" :  [],
            "platform": platform.system(),
        }

def resolve_dir(path_to_resolve):
    def resolve_windows_path(input_path):
        if '~/Documents' in input_path:
            # get My Documents regardless of localization
            import ctypes.wintypes

            buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            _ = ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 5, buf)

            return input_path.replace('~/Documents', buf.value)

        elif '~/' in input_path:
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

