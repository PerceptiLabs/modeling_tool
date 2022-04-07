import os
from pathlib import Path

from rygg.settings import IS_CONTAINERIZED, file_upload_dir


def translate_path_from_user(path, project_id):
    if IS_CONTAINERIZED:
        return translate_path_from_user_enterprise(path, project_id)
    else:
        return translate_path_from_user_local(path, project_id)


class PathNotAvailable(Exception):
    def __init__(self, path, project_id):
        super().__init__(f"Path {path} isn't available for project {project_id}.")


def translate_path_from_user_enterprise(raw_path, project_id):
    upload_dir = file_upload_dir(project_id)
    os.makedirs(upload_dir, exist_ok=True)

    # temporary special case: allow full paths in enterprise as long as they line up with the project directory
    if os.path.isabs(raw_path):
        # if the common path is still under the project dir, then we're ok
        common_base = os.path.commonpath([raw_path, upload_dir])
        if not os.path.isdir(common_base) or not os.path.os.path.samefile(
            common_base, upload_dir
        ):

            raise PathNotAvailable(raw_path, project_id)

        return raw_path
    else:
        # expected main case: path relative to the project dir
        return os.path.join(upload_dir, raw_path)


def translate_path_from_user_local(raw_path, project_id):
    # special case for local mode: if we get a full path, then we don't need to fix it up
    if os.path.isabs(raw_path):
        return raw_path

    resolved = _resolve_dir(raw_path, project_id)
    if os.path.isabs(resolved):
        return resolved
    else:
        return os.path.join(Path.home(), resolved)


def _resolve_dir(path_to_resolve, project_id):
    def resolve_windows_path(input_path):
        if "~/Documents" in input_path or "~\\Documents" in input_path:
            # get My Documents regardless of localization
            import ctypes.wintypes

            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            _ = ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 5, buf)

            return input_path.replace("~/Documents", buf.value)

        elif "~/" in input_path or "~\\" in input_path:
            return os.path.expanduser(input_path)

        else:
            return input_path

    try:
        import platform

        if platform.system().lower().startswith("win"):
            resolved_path = resolve_windows_path(path_to_resolve)
            return os.path.normpath(resolved_path)
        else:
            return os.path.expanduser(path_to_resolve)

    except Exception as e:
        return ""
