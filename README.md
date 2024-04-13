# idlib

idlib finds embedded copies of C/C++ libraries in open-source packages.

It is designed with the following goals in mind:
* simplicity
* small index size
* zero false positives at the cost of false negatives

For example:
```
python3 identify.py -s cmake-3.29.0/
```

Output: (library, git tag)
```
curl curl-8_5_0-248-g066ed4e51
xz v5.3.1alpha-65-g7136f173
libuv v1.44.0-5-gbae2992c
zlib v1.2.12-30-ga9e14e8
zstd 0^20210512.c730b8c5a38b9e93efc0c3639e26f18f14b82f95
```

This is achieved with a simple lookup table that associates a file's SHA-256
hash with metadata from the respective library's git repository:

```
CREATE TABLE IF NOT EXISTS files (
    sha256      TEXT PRIMARY KEY,
    library     TEXT,  -- name of the library
    path        TEXT,  -- file path, at the time of the matched commit
    commit_hash TEXT,  -- git commit that introduced this version
    commit_time TEXT,  -- git commit timestamp (ISO 8601 format)
    description TEXT   -- git describe for this commit,
                       -- ... falls back to: 0^{date}.{commit_hash}
);
```

idlib is comprised of an indexer (`index.py`) that generates the aforementioned
sqlite database, and a client (`identify.py`). Unless you want to add new
libraries, you generally don't need to run the indexer. The database is updated
and released periodically on GitHub.

## Indexer
The [indexer](index.py) goes through a list of configured libraries (see
`config.py`), and performs the following steps:

* Follow the git log for each configured file, including renamed files. For
  each file@commit:
  - store SHA-256
  - store metadata, e.g. the commit timestamp and `git describe` output

That's all.

```
usage: index.py [-h] [-d DB] [-l LIBRARY] [-v]

options:
  -h, --help            show this help message and exit
  -d DB                 database path. Default: ./idlib.sqlite
  -l LIBRARY, --library LIBRARY
                        index only a specific library
  -v, --verbose
```

## Client
The [client](identify.py) enumerates all C/C++ files in a directory, hashes
them and looks up the respective metadata in the sqlite database.

In summarize mode (`-s`), it groups the matches by library and shows only the
description of the latest match (sorted by git commit timestamp).

```
usage: identify.py [-h] [-d DB] [-s] directory

Identify embedded open-source libraries

positional arguments:
  directory        directory containing the source code to search

options:
  -h, --help       show this help message and exit
  -d DB            database path. Default: ./idlib.sqlite
  -s, --summarize  don't report individual files, just the detected libs and their most probable version respectively.
```
