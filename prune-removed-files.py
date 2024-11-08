import os
import sys
import argparse
import shutil

from datetime import datetime
from utils import to_wsl, run_command, run

def main(def_args=None):

    if def_args is None:
        def_args = sys.argv[1:]
    args = arguments(def_args)

    source_path = to_wsl(args.source)
    os.chdir(source_path)

    print("Generating list of all files in history...")
    command = "git log --diff-filter=D --name-only --pretty=format: | sort | uniq"
    output = run_command(command, capture_output=True)
    deleted_files = list(filter(None, output.splitlines()))

    print("Removing unused files with git-filter-repo...")
    remove_unused_files(deleted_files)

    print("Running garbage collection...")
    run_command(['git', 'gc', '--prune=now', '--aggressive'])

    print("Process completed.")

# def generate_current_files_list():
#     return run_command(['git', 'ls-tree', '-r', 'HEAD', '--name-only'], capture_output=True).splitlines()

# def generate_all_files_in_history_list():
#     return run_command(['git', 'log', '--diff-filter=D', '--name-only', '--pretty=format:', '|', 'sort', '|', 'uniq'], capture_output=True).splitlines()

def remove_unused_files(unused_files):
    # Prepare the filter command with all unused files
    if unused_files:
        command = ['git', 'filter-repo', '--force', '--invert-paths']
        for file in unused_files:
            command.extend(['--path', file])
        # print(command)
        run(command)


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source',
                        type=str,
                        required=True,
                        help="""Path of the directory of the source repository.""")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()