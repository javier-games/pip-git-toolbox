import os
import sys
import git
import argparse
import subprocess
from datetime import datetime
from subprocess import Popen


def main(def_args=None):
    if def_args is None:
        def_args = sys.argv[1:]
    args = arguments(def_args)

    # Convert the source path to WSL format if necessary
    source_path = convert_windows_path_to_wsl_path(args.source)

    repo = git.Repo(source_path)
    commits_list = []
    for commit in repo.iter_commits():
        commits_list.append({
            'date': commit.authored_datetime,
            'message': commit.message.strip(),
            'user_email': commit.author.email
        })
    # Get Filter email.

    if args.email_filter is not None:
        email_filter = args.email_filter
    else:
        try:
            email_filter = subprocess.check_output(['git', 'config', 'user.email']).decode('utf-8').strip()
            print("Email filter is: {}".format(email_filter))
        except subprocess.CalledProcessError as e:
            print("Error getting git config:", e)
            return None

    # Create target repository.

    if args.target is not None:
        target_directory = args.target
    else:
        current_date = datetime.now()
        target_directory = source_path + '-commitment-recovery-' + current_date.strftime('%Y-%m-%d-%H-%M-%S')

    os.mkdir(target_directory)
    os.chdir(target_directory)

    run(['git', 'init', '-b', 'main'])

    # Recover history.

    for commit in reversed(commits_list):
        if args.hide_message:
            message = commit['date'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            message = commit['message']

        if email_filter == commit['user_email']:
            git_commit(commit['date'], message)

def convert_windows_path_to_wsl_path(path):
    if sys.platform == 'linux' and os.path.exists('/mnt/c') and len(path) > 1 and path[1] == ':':
        drive_letter = path[0].lower()
        wsl_path = f'/mnt/{drive_letter}{path[2:].replace("\\", "/")}'
        return wsl_path
    return path


def git_commit(date, message):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message, '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    Popen(commands).wait()


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source',
                        type=str,
                        required=True,
                        help="""Path of the directory of the source repository.""")
    parser.add_argument('-t', '--target',
                        type=str,
                        required=False,
                        help="""Path where to create the target repository. If none, target repository will be created
                        with the name of the source repository and the -commitment-recovery-{Date} suffix.""")
    parser.add_argument('-ef', '--email_filter',
                        type=str,
                        required=False,
                        help="""Only commits signed with the given email will be considered.
                        If is none then it uses the current git config user email.""")
    parser.add_argument('-hm', '--hide_message',
                        action='store_true',
                        help="""Does not copy the commit message to the target repository.""")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()