from github import Github, InputGitTreeElement
import base64
import os

class RepoExporterAPI():
    def __init__(self, token, repo_name):
        self.git = Github(token)
        self.repo_name = repo_name.replace(" ", "-")

    def add_files(self, files: dict, commit_message):
        repo = self._get_or_make_repository()
        path_data_pairs = RepoExporterAPI._file_datas(files)
        element_list = [self._element_from_file_data(repo, file_path, data) for file_path, data in path_data_pairs]
        return [self._add_elements_to_new_commit(repo, element_list, commit_message), self._get_repo_url()]

    @staticmethod
    def _file_datas(files: dict):
        for src_path, dest_path in files.items():
            data = RepoExporterAPI._file_data(src_path)
            yield (dest_path, data)

    @staticmethod
    def _file_data(file_path):
        with open(os.path.join(file_path), "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _element_from_file_data(self, repo, file_path, data):
        sha = repo.create_git_blob(data, "base64").sha
        return InputGitTreeElement(path=file_path, mode="100644", type="blob", sha=sha)

    def _add_elements_to_new_commit(self, repo, element_list, commit_message):
        head_sha = repo.get_branch("master").commit.sha
        base_tree = repo.get_git_tree(sha=head_sha)
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(sha=head_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref = repo.get_git_ref("heads/master")
        master_ref.edit(sha=commit.sha)
        return commit.sha

    def _get_repo_url(self):
        return (f"www.github.com/{self.git.get_user.login}/{self.repo_name}")

    @staticmethod
    def _list_users_repo_names(git):
        """
        Create a list of all the repos of User

        Arguments:
            git : Github object with Oauth token

        Returns:
            List of repo of that User
        """

        # can add parameter since, visible- all/public
        return [re.name for re in git.get_user().get_repos()]

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

        repos = RepoExporterAPI._list_users_repo_names(self.git)

        user = self.git.get_user()

        repopath = user.login + "/" + self.repo_name

        if self.repo_name in repos:
            return self.git.get_repo(repopath)

        return user.create_repo(
            self.repo_name,  # name -- string
            "This repo wass created using PerceptiLabs. It contains ML models.",  # description -- string
            # "http://www.example.com", # homepage -- string
            # False, # private -- bool
            auto_init=True,
        )

