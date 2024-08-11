import os
import sys
import git
import argparse

from datetime import datetime, timedelta
from utils import to_wsl, run, copy_directory, delete_files

def main(def_args=None):

    if def_args is None:
        def_args = sys.argv[1:]
    args = arguments(def_args)

    if args.date is None or args.source is None:
        print("Invalid date or source")
        return None

    # Get Date.

    try:
        start_date = datetime.strptime(args.date, "%Y/%m/%d")
    except ValueError:
        print("Invalid date format. Please use YYYY/MM/DD format.")
        return None

    # Get repository commit history.

    source_path = to_wsl(args.source)

    try:
        repo = git.Repo(source_path)
    except git.exc.NoSuchPathError:
        print(f"Source repository path '{source_path}' does not exist.")
        return None

    if args.branch is not None:
        repo.git.checkout(args.branch)
    active_branch_name = repo.active_branch.name
    active_branch_hash = repo.active_branch.commit.hexsha

    repo_reversible = list(repo.iter_commits())
    commits_list = []
    last_commit_date = None
    for commit in reversed(repo_reversible):

        commit_date = commit.authored_datetime.replace(tzinfo=None)
        if last_commit_date is None:
            commit_offset = 0
            original_start_date = commit_date
            total_offset = (start_date-original_start_date).days + 1
            start_date = original_start_date + timedelta(days = total_offset)
        else:
            commit_offset = (commit_date - last_commit_date).days

        commit_parents = []
        for commit_parent in commit.parents:
            commit_parents.append(commit_parent.hexsha)

        commits_list.append({
            'date': commit_date,
            'days_offset': commit_offset,
            'message': commit.message.strip(),
            'hash': commit.hexsha,
            'parents': commit_parents
        })
        last_commit_date = commit_date

    # Init directory.
    current_date = datetime.now()
    os.chdir(source_path)
    os.chdir("..")
    temp_dir = os.path.join(os.getcwd(), ('time-displacement-temp' + current_date.strftime('%Y-%m-%d-%H-%M-%S')))
    if args.target is not None:
        target_directory = args.target
    else:
        target_directory = source_path + '-time-displacement-' + current_date.strftime('%Y-%m-%d-%H-%M-%S')
    os.chdir(source_path)
    temp_active_branch_name = f"temp/{active_branch_name}"

    # Recreate source.

    last_commit_date = start_date
    temp_branches = []
    for i, commit in enumerate(commits_list):

        commit_date = last_commit_date + timedelta(days=commit['days_offset'])
        commit_date_git = commit_date.strftime("%Y-%m-%d %H:%M:%S")
        print(f'Commit: {commit['hash']} {commit['date']} : {commit['parents']}' )

        temp_ref_branch = f"temp/ref/{commit['hash']}"

        if len(commit['parents']) == 0:
            print(f"No parents for commit {commit['hash']}")
            run(['git', 'stash'])
            run(['git', 'checkout', commit['hash']])
            run(['git', 'checkout', '--orphan', temp_ref_branch])
            temp_branches.append(temp_ref_branch)

            run(['git', 'add', '.'])
            run(['git', 'commit', '--message', commit['message'], '--date', commit_date_git])

        elif len(commit['parents']) == 1:

            temp_ref_parent_branch = f"temp/ref/{commit['parents'][0]}"

            run(['git', 'checkout', commit['hash']])
            copy_directory(source_path, temp_dir, [".git"])

            run(['git', 'checkout', temp_ref_parent_branch])
            run(['git', 'checkout', '-b', temp_ref_branch])
            temp_branches.append(temp_ref_branch)

            delete_files(source_path, [".git"])
            copy_directory(temp_dir, source_path, overwrite=True)
            run(['git', 'add', '.'])
            run(['git', 'commit', '--message', commit['message'], '--date', commit_date_git])

            delete_files(temp_dir)

        elif len(commit['parents']) == 2:

            temp_ref_parent_branch = f"temp/ref/{commit['parents'][0]}"

            run(['git', 'checkout', temp_ref_parent_branch])
            run(['git', 'checkout', '-b', temp_ref_branch])
            temp_branches.append(temp_ref_branch)

            run(['git', 'merge', f"temp/ref/{commit['parents'][1]}"])
            run(['git', 'add', '.'])
            run(['git', 'commit','--message', commit['message']])

            run(['git', 'checkout', commit['hash']])
            copy_directory(source_path, temp_dir, ['.git'] )

            run(['git', 'checkout', temp_ref_branch])

            delete_files(source_path, ['.git'])
            copy_directory(temp_dir, source_path, overwrite=True)
            run(['git', 'add', '.'])

            run(['git', 'commit', '--amend', '--no-edit', '--date', commit_date_git])

            delete_files(temp_dir)

        if active_branch_hash == commit['hash']:
            run(['git', 'branch', temp_active_branch_name])

        last_commit_date = commit_date

    run(['git', 'checkout', temp_active_branch_name])
    for branch in temp_branches:
        run(['git', 'branch', '-D', branch])

    os.rmdir(temp_dir)
    os.makedirs(target_directory, exist_ok=True)
    os.chdir(target_directory)
    run(['git', 'init'])
    run(['git', 'pull', source_path, temp_active_branch_name, '--no-edit'])

    os.chdir(source_path)
    run(['git', 'checkout', active_branch_name])
    run(['git', 'branch', '-D', temp_active_branch_name])


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source',
                        type=str,
                        required=True,
                        help="""Path of the directory of the source repository.""")
    parser.add_argument('-d', '--date',
                        type=str,
                        required=True,
                        help="""New starting date to rewrite the given repository.""")
    parser.add_argument('-t', '--target',
                        type=str,
                        required=False,
                        help="""Path where to create the target repository. If none, target repository will be created
                        with the name of the source repository and the -commitment-recovery-{Date} suffix.""")
    parser.add_argument('-b', '--branch',
                        type=str,
                        required=False,
                        help="""If not None, tries to checks out the branch of the source repository and rewrites the
                        history from that branch. By default it uses the current branch.""")
    return parser.parse_args(argsval)

if __name__ == "__main__":
    main()