from github import Github, GithubException, InputGitTreeElement
import os, requests, base64, github
from git import Repo, GitCommandError
from send2trash import send2trash

def list_files(path):
    """
    Creates a list of files with path in directory

    Arguments:
        path :  path to directory where readme needs to created

    Returns:
        List of files inside path
    """

    tempfiles = [os.path.join(r,file) for r,d,f in (os.walk(path)) for file in f]
    return [os.path.relpath(file, path) for file in tempfiles] # TODO: how to get the path inside the folder

def list_folders(path):

    """
    List of folders inside the path

    Arguments:
        path :  path of the folder
    """

    return [f.name for f in os.scandir(path) if f.is_dir()]

def get_reponame(url):
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
        print (Exception("Badly formatted url {}".format(url)))

    return url[last_slash + 1:last_suffix]

# add a readME file inside the folder similar to the one created in github
def create_readME(path):
    """
    Creates a readme file in directory

    Arguments:
        path :  path to directory where readme needs to created
    """

    readme_path = os.path.join(path, "README.md")

    if not os.path.exists(readme_path):
        f = open(readme_path, "x")
        f.close()

# Function needs to update the context of the Readme
def update_README(repo):

    return 0

# functions uses GITHUB API
def isRepoPublic(URL):
    """
    Check repo is public

    Arguments:
        path :  URL of the user repo
    """

    response = requests.get(URL)

    if(response.status_code == 200):
        return True
    else:
        return False

def list_repos(git):
    """
    Create a list of all the repos of User

    Arguments:
        git : Github object with Oauth token

    Returns:
        List of repo of that User
    """

    ls = list()
    for re in git.get_user().get_repos(): # can add parameter since, visible- all/public
        ls.append(re.name)
    return ls

def list_content(repo, path=""):

    """
    List all the files inside particular repo

    Arguments:
        repo :      repo object
        path :      path inside the repo

    Returns:
        List of files inside the repo
    """

    ls = list()
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            ls.append(file_content.path)

    return ls

# Might override Github module had same name
def get_repository(git, repo_name):

    """
    Function gets the repo object

    Arguments:
        git :       GitHub object using the Oauth token
        repo_name:  Name of the repo

    Returns:
        Repo object
    """

    repos = list_repos(git)

    try:
        user = git.get_user()
    except GithubException as ghe:
        print(ghe)
    
    repopath = user.login+"/"+repo_name
    
    if repo_name in repos:
        try:
            repository = git.get_repo(repopath)
        except GithubException as ghe:
            print(ghe)
    else:
        try:
            repository = user.create_repo(
                        repo_name, # name -- string
                        "This repo is created using PerceptiLabs tool it contains the ML models", # description -- string
                        # "http://www.example.com", # homepage -- string
                        # False, # private -- bool
                        auto_init=True,
                    )
        except GithubException as ghe:
            print(ghe)

    return repository

def update_repo(repo, files, path, commit, isData=False):

    """
    updates the selected repo with listed files on particular file_path

    Arguments:
        repo :      repo object which needs to upated
        files:      list of files which needs to be exported
        path :      path to particular files are saved
        commit:     Commit message for the commit tree
        isData:   Boolean object know it's a Datapath or Filepath
    """

    file_list = list_files(path)
    element_list = list()
    
    if not files:
        files = file_list

    for file in file_list:
        if os.path.basename(file) in files: #TODO : remove the os.path once you add path inside the files
            data = base64.b64encode(open(os.path.join(path, file), "rb").read())
            if isData:
                data_dir = "data"
                filepath = os.path.join(data_dir, file)
            else:   # to make a directory of data inside the repo
                filepath = file
            try:
                blob = repo.create_git_blob(data.decode("utf-8"), "base64")
                element = InputGitTreeElement(path=filepath, mode='100644', type='blob', sha=blob.sha)
            except GithubException as ghe:
                print(ghe)
            element_list.append(element)
    
    try:
        head_sha = repo.get_branch('master').commit.sha
        base_tree = repo.get_git_tree(sha=head_sha)
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(sha=head_sha)
        commit = repo.create_git_commit(commit, tree, [parent])
        master_ref = repo.get_git_ref('heads/master')
        master_ref.edit(sha=commit.sha)
    except GithubException as ghe:
        print(ghe)

def Github_Export(token, tensorpath, repo_name, setting, ls, datapath="", commit="New commit from PerceptiLabs"):

    """
    Final API call to export the files

    Arguments:
        token :         Github Oauth Token
        tensorpath :    Path to the tensor-files directory
        setting:        enum of basic or advanced settings
        ls :            it contains list of files needs to be uploaded or boolean list for [tensor-files, data-files]
        commit :        commit message from User
        datapath:       Path to the data-files directory
    """

    git = Github(token)
    repo = get_repository(git, repo_name)

    # TODO: create ReadME file inside directory and update it

    if setting == 'basic':

        update_repo(repo, ['model.json', 'README.md'], tensorpath, commit)
        
        if ls[0]:  # tensorflows files
            tensorfiles = ['model.json', 'checkpoint', 'model.ckpt-1.index', 'model.ckpt-1.data-00001-of-00002', 'model.ckpt-1.data-00000-of-00002', 'saved_model.pb', 'variables.data-00000-of-00001', 'variables.index']
            update_repo(repo, tensorfiles, tensorpath, commit)

        if ls[1]:  # datafiles files
            update_repo(repo, [], datapath, commit, True)

    elif setting == 'advanced':
        update_repo(repo, ls, tensorpath, commit) # TODO: handle the files together with Advanced function
        update_repo(repo, ls, datapath, commit)

def Github_Import(path, URL):

    '''
    Clones the passed repo to my staging dir

    Arguments:
        path:   path where repo needs to clone
        URL:    URL of the github repo
    '''

    warn = False
    is_public = isRepoPublic(URL)


    if(not is_public):
        print("Invalid URL")
    else:
        reponame = get_reponame(URL)
        repopath = os.path.join(path, reponame)
        if os.path.exists(repopath) and os.path.isdir(repopath):
            if not os.listdir(repopath):
                try:
                    Repo.clone_from(URL, repopath)
                except GitCommandError as exception:
                    print(exception)
            else:    # Can add any parameter to check it's github repo and doesn't give the warning
                print("Warning directory not empty")
                warn = True
        else:
            os.mkdir(repopath)
            try:
                Repo.clone_from(URL, repopath)
            except GitCommandError as exception:
                print(exception)
    
    # It overrides the Directory, keeps the old directory inside the trash
    # TODO: check if it's has same content of github repo, doesn't keep the old directory inside Trash
    if warn:
        print("Overriding the directory")
        try: # remove the existing directory
            send2trash(repopath)
        except OSError as error: 
            print(error)
        
        try: # creates a new directory
            os.mkdir(repopath) 
        except OSError as error: 
            print(error)
        
        try: # clone the github repo into new directory
            Repo.clone_from(URL, repopath)
        except GitCommandError as exception:
            print(exception)