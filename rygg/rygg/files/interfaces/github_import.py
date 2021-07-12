import requests
from github import Github
from rygg.files.exceptions import UserError

class RepoImporterAPI():
    def __init__(self, url):
        self.url = url

    def is_public(self):
        response = requests.head(self.url)

        if response.status_code == 200:
            return True
        else:
            return False

    def model_exist(self):
        temp = self.url
        temp = temp.replace("https://github.com/", "")
        temp = temp.replace("http://github.com/", "")
        temp = temp.replace("https://www.github.com/", "")
        temp = temp.replace("http://www.github.com/", "")
        temp = temp.replace(".git", "")

        repo = Github().get_repo(temp)
        contents = repo.get_contents("")

        for content in contents:
            if content == "model.json":
                return True

        return False

    def clone_to(self, dest_path):
        try:
            from git import Repo
        except:
            raise UserError("We can't talk to the git command. Is it installed?")

        Repo.clone_from(self.url, dest_path)

