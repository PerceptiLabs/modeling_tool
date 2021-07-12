from rygg.files.interfaces.github_import import RepoImporterAPI
from rygg.files.exceptions import UserError
import os, requests
from send2trash import send2trash


def _create_README(tensorpath):
        file_url = {
            "README.md": "https://github.com/PerceptiLabs/ExportTemplate/raw/master/README.md",
            "pl_logo.png": "https://github.com/PerceptiLabs/ExportTemplate/raw/master/pl_logo.png"
        }
        for file in file_url:
            obj = requests.get(file_url[file])
            with open(os.path.join(tensorpath, file), "wb") as file:
                file.write(obj.content)
                file.close()


def _list_files(root_path):
        """
        Creates a list of files with path in directory

        Arguments:
            root_path :  path to directory where readme needs to created

        Returns:
            List of files inside path
        """

        tempfiles = [os.path.join(r, filename) for r, d, f in (os.walk(root_path)) for filename in f]
        file_list = [os.path.relpath(filename, root_path) for filename in tempfiles]
        return [file.replace(os.sep, '/') for file in file_list]


def _selected_files(root_path, requested_files):
    file_list = _list_files(root_path)

    for file_path in file_list:
        if (file_path in requested_files):
            if not os.path.basename(file_path).startswith("."):
                yield file_path

def _selected_files_dict(base_path, filenames_list):
    file_paths = _selected_files(base_path, filenames_list)
    return { os.path.join(base_path, f) : f for f in file_paths }

def _base_files(tensorpath):
        return _selected_files_dict(tensorpath, [
            "model.json",
            "README.md",
            "pl_logo.png"
            ])


def build_export_dict(tensorpath, add_training_files: bool, datapaths=[]):
    """
    Build a dict of files to export with mapping: <local_path> -> <path in repo>

    Arguments:
        tensorpath         : Path to the tensor-files directory
        add_training_files : Whether to add training files to the commit
        datapath           : Path to the data-files directory
    """

    def _all_files_to_export(root_path):
        file_list = _list_files(root_path)

        for file_path in file_list:
            if not os.path.basename(file_path).startswith("."):
                yield file_path

    def _training_files(tensorpath):
        return _selected_files_dict(tensorpath,_all_files_to_export(tensorpath))

    def _data_files(datapath):
        if os.path.isdir(datapath):
            dir_name = os.path.basename(datapath)
            return {os.path.join(datapath, f) : f"data/{dir_name}/{f}" for f in _all_files_to_export(datapath)}
        elif os.path.isfile(datapath):
            return {datapath : f"data/{os.path.basename(datapath)}"}
        return {}

    to_export = _base_files(tensorpath)
    if add_training_files:
        to_export = {**to_export, **_training_files(tensorpath)}

    for datapath in datapaths:
        to_export = {**to_export, **_data_files(datapath)}

    return to_export

def build_advanced_export_dict(tensorpath, datapaths=[], tensorfiles=[], datafiles=[]):
    """
    Build a dict of files to export with mapping: <local_path> -> <path in repo>

    Arguments:
        tensorpath         : Path to the tensor-files directory
        datapath           : Path to the data-files directory
        tensorfiles        : list of Model directory files
        datafiles          : list of data directory files
    """

    def _training_files(tensorpath, tensorfiles):
        return _selected_files_dict(tensorpath, tensorfiles)


    def _data_files(datapath , datafiles):
        return {os.path.join(datapath, f) : f"data/{f}" for f in datafiles}


    to_export = _base_files(tensorpath)
    if tensorfiles:
        to_export = {**to_export, **_training_files(tensorpath, tensorfiles)}

    for datapath in datapaths:
        to_export = {**to_export, **_data_files(datapath, datafiles)}

    return to_export

def export_repo_basic(
    exporter_api,
    tensorpath : str,
    add_training_files : bool,
    datapaths: list,
    commit_message="New commit from PerceptiLabs",
):

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


def export_repo_advanced(
    exporter_api,
    tensorpath : str,
    tensorfiles: list, 
    datafiles: list,
    datapaths: list,
    commit_message="New commit from PerceptiLabs",
):

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
    to_export = build_advanced_export_dict(tensorpath, datapaths=datapaths, tensorfiles=tensorfiles, datafiles=datafiles)
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
            raise UserError(f"Error while sending the repo to the trash: {repopath}", error)

        try:  # create a new directory
            os.mkdir(repopath)
        except OSError as error:
            raise UserError(f"Error while making new directory: {repopath}", error)

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
            raise UserError("Badly formatted url {}".format(url))

        return url[last_slash + 1 : last_suffix]

    api = RepoImporterAPI(url)
    if not api.is_public():
        raise UserError("Invalid URL")

    if api.model_exist():
        raise UserError("No model file found")

    reponame = parse_reponame(url)
    dest_path = os.path.join(path, reponame)


    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    if not os.path.isdir(dest_path):
        raise UserError(f"{dest_path} exists but isn't a directory")

    if os.listdir(dest_path):
        if not overwrite:
            raise UserError(f"Path {dest_path} isn't empty. Pass overwrite=True to overwrite")

        prep_nonempty_dir_for_clone(dest_path)

    api.clone_to(dest_path)

def create_issue(api, title, body):
    
    if api.issue_type == "invalid":
        raise UserError("Invalid Issue type")

    return api._create_issue(title,body)
