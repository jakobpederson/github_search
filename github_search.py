from github import Github, GithubException


def get_requirements(user, repo):
    repos = user.get_repos()
    branches = []
    file_contents = []
    for branch in repo.get_branches():
       branches.append(branch)
       file_content = get_file_contents(repo, 'requirements', branch.name)
       file_contents.extend(file_content if file_content else [])
       file_data = [file_content.decoded_content.decode("utf-8").split('\n') for file_content in file_contents]
    return filter_file_contents(file_data, repo.name, branch.name)

def get_file_contents(repo, file_path, branch_name):
    try:
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException as e:
        print(e)


def filter_file_contents(file_data, repo_name, branch_name):
    result = []
    for lst in file_data:
        reqs = [repo_name, branch_name] + [val for val in lst if val and val[0] != '-' and val[0] != '#']
        result.append(reqs)
    return result

