#!/usr/bin/env python3
from pathlib import Path
import argparse
import collections
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import hashlib
import sqlite3
import sys

from git import GitRepo
import config


# try:
#     import magic
#     def mime_type_from_blob(blob):
#         return magic.from_buffer(blob, mime=True)
# except ModuleNotFoundError:
#     print("python-magic not found, falling back /usr/bin/file",
#           file=sys.stderr)
#     import subprocess
#     def mime_type_from_blob(blob):
#         proc = subprocess.run(['file', '-b', '--mime-type', '-'],
#             capture_output=True, text=True, input=blob, check=True)
#         return proc.stdout.strip()


def libpath(lib):
    return Path("libraries") / lib.name


# Normalization could save a bit of space but not that much. Only `time` and
# `commit_desc` could be in a separate table. Not worth it, IMHO. It's much
# easier to query a single table.
SCHEMA = '''
CREATE TABLE IF NOT EXISTS files (
    sha256      TEXT,
    library     TEXT,  -- name of the library
    commit_hash TEXT,  -- git commit that introduced this version
    commit_time TEXT,  -- git commit timestamp (ISO 8601 format)
    commit_desc TEXT,  -- git describe for this commit,
                       -- ... falls back to: 0^{date}.{commit_hash}
    path        TEXT,  -- file path at the time of the matched commit
    size        INTEGER
    -- mime_type   TEXT   -- $(file -b --mime-type < blob)
);
CREATE INDEX IF NOT EXISTS files_sha256_index ON files(sha256);
CREATE INDEX IF NOT EXISTS files_library_index ON files(library);

CREATE TABLE IF NOT EXISTS libraries (  -- optional
    library     TEXT PRIMARY KEY,
    git_remote  TEXT,  -- git remote URI
    summary     TEXT   -- short summary of the library
);
'''

SourceInfo = collections.namedtuple(
        'SourceInfo', ['sha256',
                       'library',
                       'commit_hash',
                       'commit_time',
                       'commit_desc',
                       'path',
                       'size',
                       # 'mime_type'
                       ])


parser = argparse.ArgumentParser()
parser.add_argument("-d", help="database path. Default: ./idlib.sqlite",
                    dest="db", default='idlib.sqlite')
parser.add_argument("-l", "--library", help="index only a specific library")
parser.add_argument("--prune-only", action="store_true",
                    help="only prune the database")
parser.add_argument("--no-prune", action="store_true",
                    help="don't prune the database")
parser.add_argument("-m", "--mode",
                    choices=["sparse", "full"], default="sparse",
                    help="index mode (default: sparse)")
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
    print("OK")
print()


con = sqlite3.connect(args.db)
cur = con.executescript(SCHEMA)


def get_sourceinfos(git, lib_name, commitinfo):
    result = []
    commit_hash, commit_time, paths, _ = commitinfo
    commit_desc = git.describe(commit_hash)
    if not commit_desc:
        commit_desc = "0^" + commit_time.strftime("%Y%m%d.") + commit_hash
    for path in paths:
        blob = git.file_bytes_at_commit(commit_hash, path)
        file_size = len(blob)
        m = hashlib.sha256()
        m.update(blob)
        sha256 = m.hexdigest()
        # mime_type = mime_type_from_blob(blob)
        result.append(SourceInfo(sha256=sha256,
                                 library=lib_name,
                                 commit_hash=commit_hash,
                                 commit_time=commit_time,
                                 commit_desc=commit_desc,
                                 path=path,
                                 size=file_size,
                                 # mime_type=mime_type
                                 ))
    # print(f"{cnt_commits}/{len(commits)} commits  {cnt_hashes} hashes",
    #       end='\r')
    return result

def get_all_sourceinfos(git, lib_name, commitinfos):
    result = []
    for ci in commitinfos:
       result += get_sourceinfos(git, lib_name, ci)
    return result

def get_all_sourceinfos_parallel(git, lib_name, commitinfos):
    result = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_sourceinfos, git, lib_name, ci) for ci in commitinfos]
        for future in concurrent.futures.as_completed(futures):
            result += future.result()
    return result

def index_full():
    for lib in libraries:
        print(f"Indexing library: {lib.name}")
        sys.stdout.flush()
        git = GitRepo(libpath(lib))
        print("- fetching list of all commits")
        commitinfos = git.all_commits_with_metadata()
        # commit_hashes = list(map(lambda c: c[0], commits))
        num_files = 0
        for ci in commitinfos:
            num_files += len(ci.paths)
        print(f"- hashing {num_files} files in {len(commitinfos)} commits")
        sourceinfos = get_all_sourceinfos_parallel(git, lib.name, commitinfos)
        cur = con.cursor()
        cur.execute('DELETE FROM files WHERE library = ?', (lib.name,))
        for info in sourceinfos:
            cur.execute('''INSERT INTO files VALUES (?,?,?,?,?,?,?)''', info)
        con.commit()
        print()
        sys.stdout.flush()


def index_sparse():
    for lib in libraries:
        print(f"Indexing library: {lib.name}")
        sys.stdout.flush()
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
                                                 commit_hash=commit,
                                                 commit_time=commit_time,
                                                 commit_desc=description,
                                                 path=path,
                                                 size=len(blob)
                                                 )

                if args.verbose:
                    print(f"{lib.name} {commit} {commit_time} {path} {description}")

        print(f"collected {len(sourceinfos)} hashes.")
        for info in sourceinfos.values():
            cur.execute('''INSERT INTO files VALUES (?,?,?,?,?,?,?)''', info)
        con.commit()
        print()
        sys.stdout.flush()


def prune():
    cur = con.cursor()
    print("Pruning database...")

    print("- delete empty files")
    cur.execute('DELETE FROM files WHERE size == 0')
    print(f"  - deleted {cur.rowcount} empty files")
    con.commit()

    print("- delete embedded copies")
    for a_lib, b_libs in config.embedded.items():
        for b_lib in b_libs:
            print(f"  - {a_lib} -= {b_lib}")
            to_delete = []
            rows = cur.execute('''SELECT a.library, a.sha256, a.path FROM files a JOIN files b ON a.sha256 = b.sha256 WHERE a.library = ? AND b.library = ?;''', (a_lib, b_lib))
            for row in rows:
                lib, sha256, path = row
                to_delete.append((sha256, lib))
                print(f"    - delete in {a_lib}: {sha256} {path}")
            for sha256, lib in to_delete:
                cur.execute("DELETE FROM files WHERE sha256 = ? AND library = ?", (sha256, lib))
    con.commit()

    print("- delete remaining duplicates: (check this list carefully)")
    cur = con.cursor()
    to_delete = []
    rows = cur.execute('''SELECT a.library,b.library,a.sha256,a.path FROM files a JOIN (SELECT sha256,library,path,COUNT(*) c FROM files GROUP BY sha256 HAVING c > 1) b ON a.sha256 = b.sha256 WHERE a.library != b.library AND a.size > 0 ORDER BY a.library DESC;''')
    for row in rows:
        a_lib, b_lib, sha256, a_path = row
        to_delete.append(sha256)
        print(f"  - delete duplicate: ({a_lib} <--> {b_lib}) {sha256} {a_path}")
    for sha256 in to_delete:
        cur.execute("DELETE FROM files WHERE sha256 = ?", (sha256,))
    con.commit()

    print("- vacuum")
    cur = con.cursor()
    cur.execute("VACUUM;")
    con.commit()


if not args.prune_only:
    if args.mode == 'sparse':
        index_sparse()
    elif args.mode == 'full':
        index_full()
if not args.no_prune:
    print()
    prune()

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
