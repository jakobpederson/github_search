from unittest import TestCase, mock
from github import Github, GithubException
import logging

import settings
from github_search import get_requirements

logging.disable(logging.CRITICAL)


TEST_REPOS = [
    "repo_1",
    "repo_2",
    "repo_3",
]

class GithubSearchTest(TestCase):

    def setUp(self):
        self.g = Github(settings.GITHUB_TOKEN)
        self.user = self.g.get_user()
        for repo_name in TEST_REPOS:
            try:
                self.user.create_repo(name=repo_name, auto_init=True)
            except GithubException:
                pass
        repo  = self.user.get_repo("repo_1")
        content = 'a==1234\nb>2234,<=2235\nc>3234\n- def.txt\n\n#'
        message = 'corn'
        path = "/requirements/text.txt"
        repo.create_file(
           path=path,
           message=message,
           content=content,
           branch='master'
        )

    def create_branch(self, repo):
        sha = repo.get_git_ref('heads/master').object.sha
        return repo.create_git_ref('refs/heads/{}'.format('branch_1'), sha)


    def tearDown(self):
        for repo_name in TEST_REPOS:
            try:
                self.user.get_repo(repo_name).delete()
            except GithubException:
                pass

    def test_x(self):
        result = []
        repo = self.user.get_repo("repo_1")
        result = get_requirements(self.user, repo)
        expected = [['repo_1', 'master', 'a==1234', 'b>2234,<=2235', 'c>3234']]
        self.assertCountEqual(result, expected)
        self.fail('x')