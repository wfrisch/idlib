#!/usr/bin/env python3
import os
import subprocess
import re
from datetime import datetime


def is_git_repository(directory):
    if not os.path.isdir(directory):
        return False
    try:
        subprocess.run(['git', '-C', directory, 'status'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


class GitException(Exception):
    pass


class GitRepo:
    def __init__(self, repo):
        if not is_git_repository(repo):
            raise ValueError(f"not a git repository: {repo}")
        self.repo = repo

    def is_modified(self):
        output = subprocess.check_output(['git', '-C', self.repo, 'status'])
        return "nothing to commit" not in output.decode()

    def ls_tracked_files(self):
        return subprocess.check_output(['git', '-C', self.repo, 'ls-files',
                                        '--cached']).decode().splitlines()

    def current_hash(self):
        return subprocess.check_output(['git', '-C', self.repo, 'rev-parse',
                                        'HEAD']).decode().strip()

    def commits_affecting_file(self, path):
        """List of commits that changed a file"""
        out = subprocess.check_output(['git', '-C', self.repo, 'log',
                                       '--pretty=format:%H', path])
        return out.decode('UTF-8').splitlines()

    def commits_affecting_file_follow(self, path):
        """List of commits for a file, including renames.
        Returns [(commit,path), (commit,path), ...]"""
        cmdline = ['git', '-C', self.repo, 'log', '--pretty=format:%H',
                   '--name-only', '--follow', '--diff-filter=AMR', '--', path]
        proc = subprocess.run(cmdline, capture_output=True, text=True)
        chunks = proc.stdout.strip().split('\n\n')
        return [tuple(chunk.split('\n')) for chunk in chunks]

    def file_bytes_at_commit(self, commit, path):
        """File contents for commit:path as bytes."""
        return subprocess.check_output(['git', '-C', self.repo, 'show',
                                        f'{commit}:{path}'])

    def file_text_at_commit(self, commit, path):
        """File contents for commit:path as UTF-8."""
        cmdline = ['git', '-C', self.repo, 'show', f'{commit}:{path}']
        proc = subprocess.run(cmdline, capture_output=True)
        if proc.returncode != 0:
            raise GitException("`git show` failed with exit code "
                               f"{proc.returncode}. cmdline: {cmdline}")
        return proc.stdout.decode('UTF-8', errors='ignore')  # deliberate

    def describe(self, commit):
        cmdline = ['git', '-C', self.repo, 'describe', '--candidates=100000',
                   commit]
        proc = subprocess.run(cmdline, capture_output=True, text=True)
        if re.match(r"fatal: No( annotated)? tags can describe.*",
                    proc.stderr):
            return None
        if re.match(r"fatal: No names found, cannot describe anything.*",
                    proc.stderr):
            # This happens when a repo doesn't contain any tags at all.
            return None
        if proc.returncode != 0:
            raise GitException("`git describe` failed with exit code "
                               f"{proc.returncode}. cmdline: {cmdline}")
        return proc.stdout.strip()

    def datetime(self, commit):
        time_str = subprocess.check_output(['git', '-C', self.repo, 'show',
                                            '--no-patch', '--format=%ci',
                                            commit], text=True)
        return datetime.fromisoformat(time_str.strip())

    def first_commit(self):
        proc = subprocess.run(['git', '-C', self.repo, 'rev-list',
                               '--max-parents=0', 'HEAD'], capture_output=True,
                              text=True)
        return proc.stdout.strip()

    def count_commits(self):
        proc = subprocess.run(['git', '-C', self.repo, 'rev-list', '--count',
                               'HEAD'], capture_output=True, text=True)
        return int(proc.stdout.strip())


# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
