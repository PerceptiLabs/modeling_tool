import requests
from github import Github

class CreateIssueAPI():
    def __init__(self, token, issue_type):

        self.issue_type = issue_type
        if issue_type == "normal":
            self.token = token
        elif issue_type == "anonymous":
            self.token = "5d0b894e389038b9eb18ac0bb6df9cec312d3a4a"
        else:
            self.issue_type = "invalid"

    def _create_issue(self, title, body):

        g = Github(self.token)
        repo = g.get_repo("PerceptiLabs/PerceptiLabs")
        issue = repo.create_issue(title=title, body=body)

        return issue.number
