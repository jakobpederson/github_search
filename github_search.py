from github import Github, GithubException


def get_requirements(repo, branch):
    file_contents = []
    file_content = get_file_contents(repo, 'requirements', branch.name)
    file_contents.extend(file_content if file_content else [])
    file_data = [file_content.decoded_content.decode("utf-8").split('\n') for file_content in file_contents]
    return filter_file_contents(file_data, repo.name, branch.name)

def get_file_contents(repo, file_path, branch_name):
    try:
        return repo.get_dir_contents(file_path, branch_name)
    except GithubException as e:
        print('Get File Error: {}'.format(e))


def filter_file_contents(file_data, repo_name, branch_name):
    result = []
    for lst in file_data:
        reqs = [repo_name, branch_name] + [val for val in lst if val and val[0] != '-' and val[0] != '#']
        result.append(reqs)
    return result

