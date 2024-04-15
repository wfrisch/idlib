#!/usr/bin/env python3
import re
import sys
import json
import argparse
from pathlib import Path

from git import GitRepo


class Candidate:
    def __init__(self, repo, path):
        self.repo = repo
        self.path = str(path)
        self.num_commits = None
        self.dt_latest = None
        self.dt_oldest = None

        commits = self._commits()
        self.num_commits = len(commits)
        self.dt_latest = self.repo.datetime(commits[0])
        self.dt_oldest = self.repo.datetime(commits[-1])

        self.time_cov = self._time_coverage()
        self.commit_cov = self._commit_coverage()
        self.score = self.time_cov * self.commit_cov

    def _commits(self):
        return [x[0] for x in git.commits_affecting_file_follow(relpath)]

    def _time_coverage(self) -> float:  # [0..1]
        dt_repo_oldest = self.repo.datetime(self.repo.first_commit())
        dt_repo_latest = self.repo.datetime(self.repo.current_hash())
        repo_delta = dt_repo_latest - dt_repo_oldest
        this_delta = self.dt_latest - self.dt_oldest
        coverage = this_delta.total_seconds() / repo_delta.total_seconds()
        return coverage

    def _commit_coverage(self) -> float:  # [0..1]
        return self.num_commits / self.repo.count_commits()


parser = argparse.ArgumentParser(
        prog="metric.py",
        description="helps with the file selection for new libraries")
parser.add_argument("repo_path", help="path to a git repository")
parser.add_argument("-l", "--limit", type=int, default=20,
                    help="limit the number of results. default: 20")
args = parser.parse_args()

repo_path = Path(args.repo_path)
assert repo_path.is_dir()
git = GitRepo(repo_path)

re_cc_filename = re.compile(r'.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$', re.I)

candidates = []
for path in repo_path.glob('**/*'):
    relpath = path.relative_to(repo_path)
    if re_cc_filename.match(path.name) and path.is_file():
        c = Candidate(git, str(relpath))
        candidates.append(c)

candidates.sort(key=lambda c: c.score, reverse=True)
print("Score  TimeCov  CommitCov  Path")
for c in candidates[:args.limit]:
    print(f"{c.score:.3f}  {c.time_cov:.3f}    {c.commit_cov:.3f}      {c.path}")

print()
print("Suggested config:")
paths = [c.path for c in candidates[:args.limit]]
print(json.dumps(paths, indent=4))

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
