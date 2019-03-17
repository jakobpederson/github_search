from github import Github, GithubException
from argparse import ArgumentParser
import ttd


def get_requirements(repo):
    file_contents = []
    for branch in repo.get_branches():
        file_content = get_file_contents(repo, 'requirements', branch.name)
        file_contents.extend(file_content if file_content else [])
    try:
        file_data = [content.decoded_content.decode("utf-8").split('\n') for content in file_contents]
    except AttributeError as e:
        pass
    return filter_file_contents(file_data, repo.name, branch.name)


def get_file_contents(repo, file_path, branch_name):
    try:
        print(repo.name)
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException as e:
        pass


def filter_file_contents(file_data, repo_name, branch_name):
    result = []
    for lst in file_data:
        reqs = [repo_name, branch_name] + [val for val in lst if val and val[0] != '-' and val[0] != '#']
        result.append(reqs)
    return result


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    g = Github(args.token)
    repos = g.get_user().get_repos()
    result = []
    for repo in ttd.ttd(list(repos)):
        result.append(get_requirements(repo))
    print(result)
