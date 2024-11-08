import os
import sys
import argparse
import shutil

from datetime import datetime
from utils import to_wsl, run, create_missing_directories

def main(def_args=None):

    if def_args is None:
        def_args = sys.argv[1:]
    args = arguments(def_args)

    source_path = to_wsl(args.source)

    files_with_dates = {}
    for root, _, files in os.walk(source_path):
        for file in files:
            target_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(target_file_path, source_path)
            mod_time = os.path.getmtime(target_file_path)
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H')
            if mod_date not in files_with_dates:
                files_with_dates[mod_date] = []
            files_with_dates[mod_date].append(relative_path)

    if args.target is not None:
        target_directory = args.target
    else:
        current_date = datetime.now()
        target_directory = source_path + '-history-builder-' + current_date.strftime('%Y-%m-%d-%H-%M-%S')

    os.mkdir(target_directory)
    os.chdir(target_directory)

    run(['git', 'init', '-b', 'main'])

    # Recover history.
    for date in sorted(files_with_dates.keys(), key=lambda d: datetime.strptime(d, '%Y-%m-%d %H')):
        for relative_path in files_with_dates[date]:
            source_file_path = os.path.join(source_path, relative_path)
            target_file_path = os.path.join(target_directory, relative_path)
            create_missing_directories(target_file_path)
            shutil.copy(source_file_path, target_file_path)
            time_stamp = datetime.strptime(date, '%Y-%m-%d %H').timestamp()
            os.utime(target_file_path, (time_stamp, time_stamp))
            run(['git', 'add', target_file_path])
        run(['git', 'commit', '-m', f"Added files in {date}", '--date', date])

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
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()