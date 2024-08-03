# Git Commitment Recover

The script effectively replicates the commit history from one repository to another, filtering commits based on the 
author's email and optionally hiding commit messages. It's useful for keep your Contribution Graph up to date with the 
changes made in another private repository without compromising information.

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
- `-s`/`--source`: The path to the source Git repository (required).
- `-t`/`--target`: The path where the target repository will be created (optional).
- `-ef`/`--email_filter`: An email filter to select commits by the author's email (optional).
- `-hm`/`--hide_message`: A flag to hide the commit messages in the target repository.

### Sample

```shell
python git-commitment-recover.py --source \path\to\repository\directory --email_filter email@address.com --hide_message
```

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