from github import Github, GithubException
from argparse import ArgumentParser
import ttd
import settings
from multiprocessing import Pool
import csv


def get_requirements(repo):
    file_contents = []
    result = []
    for branch in [branch for branch in repo.get_branches() if branch.name.lower() in ['production', 'master']]:
        file_content = get_file_contents(repo, 'requirements', branch.name)
        file_contents.extend(file_content if file_content else [])
        file_data = [decode(content) for content in file_contents]
        result.extend(filter_file_contents(file_data, repo.name, branch.name))
    return result


def decode(content):
    return content.decoded_content.decode("utf-8").split('\n')


def get_file_contents(repo, file_path, branch_name):
    try:
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException as e:
        pass


def filter_file_contents(file_data, repo_name, branch_name):
    result = []
    for lst in file_data:
        reqs = [repo_name, branch_name] + [val for val in lst if val and val[0] != '-' and val[0] != '#']
        result.extend(reqs)
    return result


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    g = Github(args.token)
    repos = list(g.get_user().get_repos())
    chunks = [repos[i:i + 25] for i in range(0, len(repos), 25)]
    result = []
    p = Pool(3)
    for count, repos in enumerate(chunks):
        print('loop {}'.format(count))
        result.extend(p.map(get_requirements, repos))
    rows =[x for x in result if x]
    with open("output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(rows)
