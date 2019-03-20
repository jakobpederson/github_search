from argparse import ArgumentParser
from collections import defaultdict
import csv
from github import Github, GithubException
from itertools import chain
from multiprocessing import Pool
import simplejson as json
import re


def get_requirements(repo):
    file_contents = []
    result = []
    for branch in [branch for branch in repo.get_branches() if branch.name.lower() in ['production', 'master']]:
        file_content = get_file_contents(repo, 'requirements', branch.name)
        file_contents.extend(file_content if file_content else [])
        file_data = [decode(content) for content in file_contents]
        result.extend(filter_file_contents(file_data, repo.name, branch.name))
    return result


def create_json(lst):
    response = defaultdict(lambda: defaultdict(dict))
    for val in lst:
        response[val[0]][val[1]][val[2]] = val[3:]
    return response


def decode(content):
    return content.decoded_content.decode("utf-8").split('\n')


def get_file_contents(repo, file_path, branch_name):
    try:
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException:
        pass


def filter_file_contents(file_data, repo_name, branch_name):
    result = []
    for lst in file_data:
        reqs = split_versions(repo_name, branch_name, lst)
        result.extend(reqs)
    return result


def split_versions(repo_name, branch_name, lst):
    return [[repo_name, branch_name] + re.sub(r'(?<!,)([=<>])', r',\1', val, count=1).split(',') for val in lst if val and val[0] != '-' and val[0] != '#']


def write_to_file(rows):
    with open("output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def process_repo_data(repos):
    result = []
    chunks = [repos[i:i + 20] for i in range(0, len(repos), 20)]
    p = Pool(5)
    for count, repos in enumerate(chunks, 1):
        print('loop {}'.format(count))
        result.extend(p.map(get_requirements, repos))
    rows = list(chain.from_iterable([x for x in result if x]))
    data = create_json(rows)
    return rows, data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    g = Github(args.token)
    repos = list(g.get_user().get_repos())
    rows, data = process_repo_data(repos)
    with open('delete.txt', 'w') as f:
        f.write(json.dumps(json_data))
    print(json.dumps(data))
