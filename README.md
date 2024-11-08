# Git Toolbox

## Prune Files

This script automates the cleanup of unused or deleted files from a Git repository. It identifies files that have been deleted throughout the repository’s history and removes them to reduce the repository size. The script also runs Git garbage collection to optimize repository performance. Here’s a breakdown of its main functionality:

## Commitment Recovery

The script effectively replicates the commit history from one repository to another, filtering commits based on the 
author's email and optionally hiding commit messages. It's useful for keep your Contribution Graph up to date with the 
changes made in another private repository without compromising information.

## Time Displacement

This script  is designed to create a new Git repository by replaying the commit history from an existing source 
repository. It adjusts the commit timestamps to align with a specified start date while preserving the relative 
differences in days between commits.

## History Builder

Takes from the source path the files and creates a new repository commiting them in by their last modification date.

## Requirements

### Python

Python 3.x is required since the script uses syntax and libraries compatible with Python 3.
Ensure that gitpython and other standard libraries (os, sys, argparse, subprocess, datetime) are available. 
It can be installed via pip:

```shell
pip install gitpython
```

### Git

Git must be installed and accessible from the command line since the script uses Git commands through
subprocess and interacts with Git repositories via the gitpython library.

Make sure the git global confing file has the name and email assigned.

```shell
git config --global user.name "Full Name"
```

```shell
git config --global user.email "email@address.com"
```

## Usage

The script accepts several command-line arguments:

### Commitment Recovery

- `-s`/`--source`: The path to the source Git repository (required).
- `-t`/`--target`: The path where the target repository will be created (optional).
- `-ef`/`--email_filter`: An email filter to select commits by the author's email (optional).
- `-hm`/`--hide_message`: A flag to hide the commit messages in the target repository (optional).

```shell
python commitment-recovery.py --source \path\to\repository\directory --email_filter email@address.com --hide_message
```

### Time Displacement

- `-s`/`--source`: The path to the source Git repository (required).
- `-d`/`--date`: New starting date to rewrite the given repository (required).
- `-t`/`--target`: The path where the target repository will be created (optional).
- `-b`/`--branch`: Specifies which branch to use to recreate the history.

```shell
python time-displacement.py --source \path\to\repository\directory --date YYYY/MM/DD
```

#### Limitations
Since construct the new history by coping and removing files from the source to avoid merge conflict resolutions,
the bigger the repository the longest it takes to complete.

## License
Git Commitment Recover is available under the MIT license. See the [LICENSE](LICENSE.md) file for more info.

## Contribution

All pull requests are accepted:
- Fork the repo and create your branch from develop.
- If you've added code that should be tested, add tests.
- Make sure your code lints.
- Submit a pull request!

## Support

For any questions or issues, please open a new issue on this repository.