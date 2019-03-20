from unittest import TestCase, mock
from github import Github, GithubException
import logging

import settings
from github_search import get_requirements, write_to_file, create_json, process_repo_data

logging.disable(logging.CRITICAL)


TEST_REPOS = [
    "repo_1",
]


class GithubSearchTest(TestCase):

    def setUp(self):
        self.g = Github(settings.GITHUB_TOKEN)
        self.user = self.g.get_user()
        for repo_name in TEST_REPOS:
            try:
                self.user.create_repo(name=repo_name, auto_init=True)
            except GithubException:
                print('Creation failed')
        repo = self.user.get_repo("repo_1")
        content = 'a==1234\nb>2234,<=2235\nc>3234\n- def.txt\n\n#'
        message = 'corn 2'
        path = "/requirements/text.txt"
        try:
            repo.create_file(
                path=path,
                message=message,
                content=content,
            )
        except GithubException:
            pass

    def create_branch(self, repo):
        sha = repo.get_git_ref('heads/master').object.sha
        return repo.create_git_ref('refs/heads/{}'.format('branch_1'), sha)

    def tearDown(self):
        for repo_name in TEST_REPOS:
            try:
                self.user.get_repo(repo_name).delete()
            except GithubException:
                print('failed to delete {}'.format(repo_name))

    def test_get_requirements_gets_requirements_string(self):
        result = []
        repo = self.user.get_repo("repo_1")
        result = get_requirements(repo)
        expected = [
            ['repo_1', 'master', 'a', '==1234'],
            ['repo_1', 'master', 'b', '>2234', '<=2235'],
            ['repo_1', 'master', 'c', '>3234'],
        ]
        self.assertCountEqual(result, expected)

    def test_create_json(self):
        result = []
        repo = self.user.get_repo("repo_1")
        response = get_requirements(repo)
        branch = [x for x in repo.get_branches() if x.name == 'master'][0]
        result = create_json(response)
        expected = {'repo_1': {'master': {'a': ['==1234'], 'b': ['>2234', '<=2235'], 'c': ['>3234']}}}
        self.assertCountEqual(result, expected)

    def test_process_repo_data(self):
        result = []
        repo = self.user.get_repo("repo_1")
        rows, data = process_repo_data([repo])
        self.assertCountEqual(rows, [['repo_1', 'master', 'a', '==1234'], ['repo_1', 'master', 'b', '>2234', '<=2235'], ['repo_1', 'master', 'c', '>3234']])
        self.assertEqual(data, {'repo_1': {'master': {'a': ['==1234'], 'b': ['>2234', '<=2235'], 'c': ['>3234']}}})

    def test_write_to_file(self):
        data = [['a', 'b', 'c'], ['e', 'f', 'g']]
        write_to_file(data)
        output = open("output.csv", "r")
        result = output.read()
        expected = "a,b,c\ne,f,g\n"
        self.assertEqual(result, expected)
