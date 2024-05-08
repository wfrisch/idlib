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

- TimeCov [0..1] lifespan of a file in the repo
- CommitCov [0..1] ratio of commits affecting a file within its lifespan
- Score [0..1] = TimeCov * CommitCov

This is a rather simple metric and developers should review and adjust the
suggestion manually.
"""
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import argparse
import collections
import json
from pathlib import Path
import re
import sys

from git import GitRepo


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


Candidate = collections.namedtuple('Candidate', 'path,score,time_cov,commit_cov')


all_commitinfos = git.all_commits_with_metadata()

def num_commits_in_timespan(git, start, end):
    cnt = 0
    for ci in all_commitinfos:
        if ci.commit_time >= start and ci.commit_time <= end:
            cnt += 1
    return cnt

def evaluate(git, path) -> float:
    print("eval:", path)
    sys.stdout.flush()
    commitinfos = git.all_commits_with_metadata(path)
    num_commits = len(commitinfos)
    dt_repo_latest = git.datetime(git.current_hash())
    dt_repo_oldest = git.datetime(git.first_commit())
    td_repo = dt_repo_latest - dt_repo_oldest

    # Time coverage [0..1]
    td = commitinfos[0].commit_time - commitinfos[-1].commit_time
    time_cov = td.total_seconds() / td_repo.total_seconds()

    # Commit coverage [0..1]
    # a) ratio of total commits
    # commit_cov = num_commits / git.count_commits()
    # b) commit ratio within file's lifetime
    ncits = num_commits_in_timespan(
        git,
        commitinfos[-1].commit_time,
        commitinfos[0].commit_time)
    if ncits > 0:
        commit_cov = num_commits / ncits
    else:
        # why is this happening for one file in the botan repo?
        # botan/src/tests/test_xof.cpp
        commit_cov = 0.0

    # Score [0..1]
    score = time_cov * commit_cov

    return Candidate(path, score, time_cov, commit_cov)


def evaluate_all(git, paths):
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(evaluate, git, path) for path in paths]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results


print("This may take a long time.")
paths = []
re_cc_filename = re.compile(r'.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$', re.I)
for path in repo_path.glob('**/*'):
    if re_cc_filename.match(path.name) and path.is_file():
        paths.append(path.relative_to(repo_path))
print(f"Evaluating {len(paths)} files...")
sys.stdout.flush()

candidates = evaluate_all(git, paths)
candidates.sort(key=lambda c: c.score, reverse=True)
print("\n")
print("Score  TimeCov  CommitCov  Path")
for c in candidates[:args.limit]:
    print(f"{c.score:.3f}  {c.time_cov:.3f}    {c.commit_cov:.3f}      {c.path}")

print()
print("Suggested config:")

#paths = [s.path for c in candidates[:args.limit]]
#print(json.dumps(paths, indent=4))

print('            [')
for c in candidates[:args.limit]:
    print(f'        "{c.path}",')
print('            ]),')

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
