#!/usr/bin/env python3
"""
Development tool to assist with file selection for new libraries.

Example session:

`./metric.py libraries/flac`

```
Score  TimeCov  CommitCov  Path
0.082  1.000    0.082      src/libFLAC/stream_encoder.c
0.064  0.998    0.064      src/libFLAC/stream_decoder.c
0.063  0.978    0.064      src/flac/encode.c
0.058  0.997    0.058      src/flac/main.c
0.043  0.997    0.043      src/flac/decode.c
0.028  0.967    0.029      src/libFLAC/format.c
0.026  0.905    0.029      src/libFLAC/metadata_iterators.c
0.025  0.965    0.026      src/libFLAC/lpc.c
0.023  0.946    0.025      src/libFLAC/cpu.c
0.023  0.965    0.024      include/FLAC/format.h
0.023  0.978    0.023      include/FLAC/stream_encoder.h
0.019  0.902    0.021      src/libFLAC/metadata_object.c
0.019  0.965    0.019      src/test_libFLAC/metadata_manip.c
0.018  0.965    0.019      src/test_libFLAC++/metadata_manip.cpp
0.018  0.905    0.020      include/FLAC/metadata.h
0.017  0.956    0.018      src/metaflac/main.c
0.017  0.965    0.017      src/libFLAC/stream_encoder_framing.c
0.017  0.965    0.017      src/libFLAC/include/private/lpc.h
0.016  0.965    0.016      include/FLAC/stream_decoder.h
0.015  0.978    0.015      src/flac/encode.h

Suggested config:
[
    "src/libFLAC/stream_encoder.c",
    "src/libFLAC/stream_decoder.c",
    "src/flac/encode.c",
    "src/flac/main.c",
    "src/flac/decode.c",
    "src/libFLAC/format.c",
    "src/libFLAC/metadata_iterators.c",
    "src/libFLAC/lpc.c",
    "src/libFLAC/cpu.c",
    "include/FLAC/format.h",
    "include/FLAC/stream_encoder.h",
    "src/libFLAC/metadata_object.c",
    "src/test_libFLAC/metadata_manip.c",
    "src/test_libFLAC++/metadata_manip.cpp",
    "include/FLAC/metadata.h",
    "src/metaflac/main.c",
    "src/libFLAC/stream_encoder_framing.c",
    "src/libFLAC/include/private/lpc.h",
    "include/FLAC/stream_decoder.h",
    "src/flac/encode.h"
]
```

- TimeCov [0..1] describes the lifespan of a file in the repo
- CommitCov [0..1] describes how many commits affected a file
  - TODO: count commits in the lifetime of the file instead of the repo
- Score [0..1] = TimeCov * CommitCov

This is a rather simple metric and developers should review and adjust the
suggestion manually.
"""
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

print("This may take a long time, depending on the repo size...")

re_cc_filename = re.compile(r'.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$', re.I)

candidates = []
for path in repo_path.glob('**/*'):
    relpath = path.relative_to(repo_path)
    if re_cc_filename.match(path.name) and path.is_file():
        c = Candidate(git, str(relpath))
        candidates.append(c)
    print(".", end='')
    sys.stdout.flush()
print("\n")

candidates.sort(key=lambda c: c.score, reverse=True)
print("Score  TimeCov  CommitCov  Path")
for c in candidates[:args.limit]:
    print(f"{c.score:.3f}  {c.time_cov:.3f}    {c.commit_cov:.3f}      {c.path}")

print()
print("Suggested config:")
paths = [c.path for c in candidates[:args.limit]]
#print(json.dumps(paths, indent=4))

print('            [')
for c in candidates[:args.limit]:
    print(f'             "{c.path}",')
print('            ]),')

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
