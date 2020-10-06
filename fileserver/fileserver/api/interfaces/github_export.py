from github import Github, InputGitTreeElement
import base64
import os
from fileserver.api.exceptions import UserError

GITHUB_MAX_MB = 100
GITHUB_MAX_SIZE = GITHUB_MAX_MB * 1024 ** 2
GITHUB_URL_FORMAT = "www.github.com/{username}/{repo_name}"

class RepoExporterAPI():
    def __init__(self, token, repo_name):
        self.git = Github(login_or_token = token, timeout=120)
        self.repo_name = repo_name.replace(" ", "-")

    # Github allows files up to 100MB
    @staticmethod
    def check_file_sizes(files: dict):
        too_big = [f for f in files if os.path.getsize(f) > GITHUB_MAX_SIZE]
        if too_big:
            raise UserError(f"This directory contains files that are too large to export to GitHub. The limit is {GITHUB_MAX_MB}MB.")


    def add_files(self, files: dict, commit_message):
        RepoExporterAPI.check_file_sizes(files)
        lazy_path_data_pairs = RepoExporterAPI._file_datas(files)

        repo = self._get_or_make_repository()
        element_list = [self._element_from_file_data(repo, file_path, data) for file_path, data in lazy_path_data_pairs]
        return [self._add_elements_to_new_commit(repo, element_list, commit_message), self._get_repo_url()]

    # Returns a lazy sequence of tuples: (destination path, base64-encoded contents)
    @staticmethod
    def _file_datas(files: dict):
        for src_path, dest_path in files.items():
            data = RepoExporterAPI._file_as_base64(src_path)
            yield (dest_path, data)

    @staticmethod
    def _file_as_base64(file_path):
        with open(os.path.join(file_path), "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _element_from_file_data(self, repo, file_path, data):
        sha = repo.create_git_blob(data, "base64").sha
        return InputGitTreeElement(path=file_path, mode="100644", type="blob", sha=sha)

    def _add_elements_to_new_commit(self, repo, element_list, commit_message):
        head_sha = repo.get_branch("main").commit.sha
        base_tree = repo.get_git_tree(sha=head_sha)
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(sha=head_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref = repo.get_git_ref("heads/main")
        master_ref.edit(sha=commit.sha)
        return commit.sha

    def _get_repo_url(self):
        return GITHUB_URL_FORMAT.format(username= self.git.get_user().login, repo_name = self.repo_name)

    def _list_users_repo_names(self):
        """
        Create a list of all the repos of User

        Returns:
            List of repo of that User
        """

        # can add parameter since, visible- all/public
        return [re.name for re in self.git.get_user().get_repos()]

    # Might override Github module had same name
    def _get_or_make_repository(self):

        """
        Function gets the repo object

        Arguments:
            git :       GitHub object using the Oauth token
            repo_name:  Name of the repo

        Returns:
            Repo object
        """

        repos = self._list_users_repo_names()

        user = self.git.get_user()

        repopath = user.login + "/" + self.repo_name

        if self.repo_name in repos:
            return self.git.get_repo(repopath)

        return user.create_repo(
            self.repo_name,  # name -- string
            "This repository was created using PerceptiLabs. It contains machine learning models.",  # description -- string
            # "http://www.example.com", # homepage -- string
            # False, # private -- bool
            auto_init=True,
        )

