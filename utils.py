import os
import sys
import shutil

from subprocess import Popen

def run(commands):
    Popen(commands).wait()

def to_wsl(path):
    if sys.platform == 'linux' and os.path.exists('/mnt/c') and len(path) > 1 and path[1] == ':':
        drive_letter = path[0].lower()
        relative_path = path[2:].replace("\\", "/");
        wsl_path = f'/mnt/{drive_letter}{relative_path}'
        return wsl_path
    return path


def copy_directory(source_path, target_path, ignore_list=None, overwrite=False):
    if ignore_list is None:
        ignore_list = []
    if not os.path.exists(source_path):
        raise ValueError(f"Source path '{source_path}' does not exist.")

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for item in os.listdir(source_path):
        source_item = os.path.join(source_path, item)
        target_item = os.path.join(target_path, item)

        if item in ignore_list:
            continue

        if os.path.isdir(source_item):
            copy_directory(source_item, target_item, ignore_list, overwrite)
        else:
            if os.path.exists(target_item):
                if overwrite:
                    shutil.copy2(source_item, target_item)
                else:
                    print(f"File '{target_item}' already exists. Skipping.")
            else:
                shutil.copy2(source_item, target_item)


def delete_files(directory, ignore_list=None):

    if ignore_list is None:
        ignore_list = []

    if not os.path.isdir(directory):
        raise ValueError(f"The provided path '{directory}' is not a directory.")

    for item in os.listdir(directory):
        path = os.path.join(directory, item)

        if item in ignore_list:
            continue

        if os.path.isfile(path):
            if sys.platform == 'linux' or sys.platform == 'darwin':
                run(['rm', '-f', path])
            else:
                run(['del', '/f', path])

        elif os.path.isdir(path):
            delete_files(path, ignore_list)
            if sys.platform == 'linux' or sys.platform == 'darwin':
                run(['rm', '-rf', path])
            else:
                run(['del', '/s', '/q', path])


def create_missing_directories(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)