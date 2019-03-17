from github import Github, GithubException
from multiprocessing import Pool
from argparse import ArgumentParser


def get_requirements(repo):
    file_contents = []
    for branch in repo.get_branches():
        file_content = get_file_contents(repo, 'requirements', branch.name)
        file_contents.extend(file_content if file_content else [])
    file_data = [content.decoded_content.decode("utf-8").split('\n') for content in file_contents]
    return filter_file_contents(file_data, repo.name, branch.name)


def get_file_contents(repo, file_path, branch_name):
    try:
        print('success')
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException as e:
        print('Get File Error: {}'.format(e))


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
    p = Pool(3)
    result = p.map(get_requirements, repos)
    print(result)
