#!/usr/bin/env python3
"""
Lookup table that maps sha256 file hashes to git commits of C/C++ libraries.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import sqlite3
import sys

from git import GitRepo
import config


def libpath(lib):
    return Path("libraries") / lib.name


SCHEMA = '''
CREATE TABLE IF NOT EXISTS files (
    sha256      TEXT PRIMARY KEY,
    library     TEXT,  -- name of the library
    path        TEXT,  -- file path, at the time of the matched commit
    commit_hash TEXT,  -- git commit that introduced this version
    commit_time TEXT,  -- git commit timestamp (ISO 8601 format)
    description TEXT   -- git describe for this commit,
                       -- ... falls back to: 0^{date}.{commit_hash}
);
CREATE INDEX IF NOT EXISTS files_sha256_index ON files(sha256);

CREATE TABLE IF NOT EXISTS libraries (  -- optional
    library     TEXT PRIMARY KEY,
    git_remote  TEXT,  -- git remote URI
    summary     TEXT   -- short summary of the library
);
'''

SourceInfo = collections.namedtuple(
        'SourceInfo', ['sha256',
                       'library',
                       'path',
                       'commit_hash',
                       'commit_time',
                       'description'])


parser = argparse.ArgumentParser()
parser.add_argument("-d", help="database path. Default: ./idlib.sqlite", dest="db",
                    default='idlib.sqlite')
parser.add_argument("-l", "--library", help="index only a specific library")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

if args.library:
    libraries = list(filter(lambda lib: lib.name == args.library,
                            config.libraries))
else:
    libraries = config.libraries


for lib in libraries:
    print(f"Checking configuration for {lib.name:15s} ", end='')
    try:
        git = GitRepo(libpath(lib))
    except ValueError as e:
        print(e)
        sys.exit(1)
    if git.is_modified():
        print("git repo not clean, aborting")
        sys.exit(1)
    for file in lib.files_of_interest:
        if not (libpath(lib) / file).exists():
            print(f"file not found: {file}")
            sys.exit(1)
    print("OK")
print()


con = sqlite3.connect(args.db)
cur = con.executescript(SCHEMA)

for lib in libraries:
    print(f"Indexing library: {lib.name}")
    git = GitRepo(libpath(lib))
    sourceinfos = {}
    for foi in lib.files_of_interest:
        for commit, path in git.commits_affecting_file_follow(foi):
            commit_time = git.datetime(commit)
            description = git.describe(commit)
            if not description:
                description = "0^" + commit_time.strftime("%Y%m%d.") + commit

            blob = git.file_bytes_at_commit(commit, path)
            m = hashlib.sha256()
            m.update(blob)
            sha256 = m.hexdigest()

            sourceinfos[sha256] = SourceInfo(sha256=sha256,
                                             library=lib.name,
                                             path=path,
                                             commit_hash=commit,
                                             commit_time=commit_time,
                                             description=description)

            if args.verbose:
                print(f"{lib.name} {commit} {commit_time} {path} {description}")

    print(f"collected {len(sourceinfos)} hashes.")
    for info in sourceinfos.values():
        cur.execute('''REPLACE INTO files VALUES (?,?,?,?,?,?)''', info)
    con.commit()
    print()

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
