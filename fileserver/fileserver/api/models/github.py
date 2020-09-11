from fileserver.api.interfaces.github_import import RepoImporterAPI
import os, shutil
from send2trash import send2trash


def build_export_dict(tensorpath, add_training_files: bool, datapaths=[]):
    """
    Build a dict of files to export with mapping: <local_path> -> <path in repo>

    Arguments:
        tensorpath         : Path to the tensor-files directory
        add_training_files : Whether to add training files to the commit
        datapath           : Path to the data-files directory
    """

    def _list_files(root_path):
        """
        Creates a list of files with path in directory

        Arguments:
            root_path :  path to directory where readme needs to created

        Returns:
            List of files inside path
        """

        tempfiles = [os.path.join(r, filename) for r, d, f in (os.walk(root_path)) for filename in f]
        return [os.path.relpath(filename, root_path) for filename in tempfiles]

    def _all_files_to_export(root_path):
        file_list = _list_files(root_path)

        for file_path in file_list:
            yield file_path

    def _selected_files(root_path, requested_files):
        file_list = _list_files(root_path)

        for file_path in file_list:
            if (os.path.basename(file_path) in requested_files):
                if not os.path.basename(file_path).startswith("."):
                    yield file_path

    def _selected_files_dict(base_path, filenames_list):
        file_paths = _selected_files(tensorpath, filenames_list)
        return { os.path.join(tensorpath, f) : f for f in file_paths }

    def _base_files(tensorpath):
        return _selected_files_dict(tensorpath, [
            "model.json",
            "README.md",
            ])

    def _training_files(tensorpath):
        return _selected_files_dict(tensorpath, [
            "model.json",
            "checkpoint",
            "model.ckpt-1.index",
            "model.ckpt-1.data-00001-of-00002",
            "model.ckpt-1.data-00000-of-00002",
            "saved_model.pb",
            "variables.data-00000-of-00001",
            "variables.index",
            ])

    def _data_files(datapath):
        if os.path.isdir(datapath):
            dir_name = os.path.basename(datapath)
            return {os.path.join(datapath, f) : f"data/{dir_name}/{f}" for f in _all_files_to_export(datapath)}
        return {os.path.join(datapath, f) : f"data/{f}" for f in _all_files_to_export(datapath)}

    to_export = _base_files(tensorpath)
    if add_training_files:
        to_export = {**to_export, **_training_files(tensorpath)}

    if datapaths:
        for datapath in datapaths:
            to_export = {**to_export, **_data_files(datapath)}

    return to_export

def export_repo_basic(
    exporter_api,
    tensorpath : str,
    add_training_files : bool,
    datapaths: list,
    commit_message="New commit from PerceptiLabs",
):

    def _create_README(tensorpath):
        if not os.path.exists(os.path.join(tensorpath, "README.md")):
            # the README is in the models dir
            readme_path = os.path.join(os.path.dirname(__file__), "README.md")
            dest = os.path.join(tensorpath, "README.md")
            shutil.copyfile(readme_path, dest)

    """
    call to export the files

    Arguments:
        exporter_api       : An object that responds to add_files(path, file_list, commit_message)
        tensorpath         : Path to the tensor-files directory
        add_training_files : Whether to add training files to the commit
        commit_message     : commit message from User
        datapath           : Path to the data-files directory
    """

    _create_README(tensorpath)
    to_export = build_export_dict(tensorpath, add_training_files, datapaths=datapaths)
    return exporter_api.add_files(to_export, commit_message)


def import_repo(path, url, overwrite=False):
    """
    Clones the passed repo to my staging dir

    Arguments:
        path      : path where repo needs to clone
        url       : URL of the github repo
        overwrite : whether to force the write on a preexisting directory
    """
    def prep_nonempty_dir_for_clone(repopath):
        """
        It overrides the Directory, keeps the old directory inside the trash
        Also, errors are rethrown as ValueError since we're here because the user is acting strange.
        TODO: check if it's has same content of github repo, doesn't keep the old directory inside Trash
        """

        try:  # remove the existing directory
            send2trash(repopath)
        except OSError as error:
            raise ValueError(f"Error while sending the repo to the trash: {repopath}", error)

        try:  # create a new directory
            os.mkdir(repopath)
        except OSError as error:
            raise ValueError(f"Error while making new directory: {repopath}", error)

    def parse_reponame(url):
        """
        Fetch Reponame from URL

        Arguments:
            URL :  URL of the user repo
        """
        last_slash = url.rfind("/")
        last_suffix = url.rfind(".git")
        if last_suffix < 0:
            last_suffix = len(url)

        if last_slash < 0 or last_suffix <= last_slash:
            raise ValueError("Badly formatted url {}".format(url))

        return url[last_slash + 1 : last_suffix]

    api = RepoImporterAPI(url)
    if not api.is_public():
        raise ValueError("Invalid URL")

    if api.model_exist():
        raise ValueError("No model file found")

    reponame = parse_reponame(url)
    dest_path = os.path.join(path, reponame)


    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    if not os.path.isdir(dest_path):
        raise ValueError(f"{dest_path} exists but isn't a directory")

    if os.listdir(dest_path):
        if not overwrite:
            raise ValueError(f"Path {dest_path} isn't empty. Pass overwrite=True to overwrite")

        prep_nonempty_dir_for_clone(dest_path)

    api.clone_to(dest_path)

def create_issue(api, title, body):
    
    if api.issue_type == "invalid":
        raise ValueError("Invalid Issue type")

    return api._create_issue(title,body)