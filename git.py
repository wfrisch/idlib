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
        root_commits = proc.stdout.splitlines()
        if len(root_commits) > 1:
            # multiple root commits are uncommon,
            # but they do occur, for example in 
            # https://github.com/google/googletest
            root_commits.sort(key=lambda c: self.datetime(c))
        return root_commits[0]

    def count_commits(self):
        proc = subprocess.run(['git', '-C', self.repo, 'rev-list', '--count',
                               'HEAD'], capture_output=True, text=True)
        return int(proc.stdout.strip())

    def all_commits_with_metadata(self, describe=False):
        result = []
        cmdline = ['git', '-C', self.repo, 'log', '--all', '--name-only',
                   '--date=iso', '--diff-filter=AMR', '--ignore-submodules',
                   '-z']
        if describe:
            cmdline += ['--format=format:%(describe:tags) %H %ad']
        else:
            cmdline += ['--format=format:%H %ad']
        proc = subprocess.run(cmdline, capture_output=True, text=True)
        # First line: {tag} {commit_hash} {commit_time}
        # {tag} may be empty
        """
        v5.4.6-106-g65b07dd5 65b07dd53d7938a60112fc4473f5cad3473e3534 2024-03-11 14:05:06 -0300
        lapi.c
        lapi.h
        ldebug.c
        ldo.c
        testes/api.lua
        """
        re_line0 = re.compile(
                r'(?P<desc>[^ ]+)?\s?(?P<hash>[0-9a-f]{40,})\s+(?P<date>.*)')

        chunks = proc.stdout.split('\0\0')
        for chunk in chunks:
            # if -z is combined with --name-only,
            # the first line ends with \n instead of \0 like the rest
            # this might be a bug in git
            lines = re.split(r'[\0|\n]', chunk)
            match = re_line0.match(lines[0])
            if not match:
                raise ValueError("unexpected line0: " + lines[0])
            commit_desc = match.group('desc') # can be None
            commit_hash = match.group('hash')
            commit_time = datetime.fromisoformat(match.group('date'))
            paths = lines[1:]
            result.append((commit_hash, commit_time, paths, commit_desc))
        return result

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
