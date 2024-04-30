# idlib

idlib finds embedded copies of C/C++ libraries in open-source packages.

## Usage example
```
# Download the latest database
wget -O- https://github.com/wfrisch/idlib/releases/latest/download/idlib.sqlite.zst |zstdcat > idlib.sqlite

# Scan a package
./identify.py -s cmake-3.29.0/

# Output
curl curl-8_5_0-248-g066ed4e51
xz v5.3.1alpha-65-g7136f173
libuv v1.44.0-5-gbae2992c
zlib v1.2.12-30-ga9e14e8
zstd 0^20210512.c730b8c5a38b9e93efc0c3639e26f18f14b82f95
```

## Implementation
At its core, idlib relies on a lookup table that associates a file's SHA-256
hash with metadata from the respective library's git repository:

```
CREATE TABLE IF NOT EXISTS files (
    sha256      TEXT,
    library     TEXT,  -- name of the library
    commit_hash TEXT,  -- git commit that introduced this version
    commit_time TEXT,  -- git commit timestamp (ISO 8601 format)
    commit_desc TEXT,  -- git describe for this commit,
                       -- ... falls back to: 0^{date}.{commit_hash}
    path        TEXT,  -- file path at the time of the matched commit
    size        INTEGER
);
```

### Indexer (`index.py`)
The indexer generates this database from a list of
[configured libraries](config.py).

```
$ ./index.py -h
usage: index.py [-h] [-d DB] [-l LIBRARY] [-p] [-m {sparse,full}] [-v]

options:
  -h, --help            show this help message and exit
  -d DB                 database path. Default: ./idlib.sqlite
  -l LIBRARY, --library LIBRARY
                        index only a specific library
  -p, --prune-only      don't index, only prune database
  -m {sparse,full}, --mode {sparse,full}
                        index mode (default: sparse)
  -v, --verbose
```

It has two modes:

#### Sparse mode
In sparse mode (default), only a hand-picked set of files is considered for
indexing. The idea is to improve the signal/noise ratio by choosing files that
a) are unique to the library, b) are unlikely to be omitted in a copy.

For each configured file, run `git log --follow`
  - For each commit:
    - store metadata (commit hash, time, `git describe`)
    - For each file modified by the commit:
      - store SHA-256(commit:path)

Advantages:
- Compact database
- Low false positive rate

Disadvantages:
- Less accurate version identification

#### Full mode
In full mode, all files in all commits are indexed.

Advantages:
- More accurate version identification

Disadvantages:
- Large database
- False positives likely, unless the client filters the results, for example by
  only considering .c/.cpp matches

#### Pruning
In both modes the indexer prunes the database after indexing:
- Remove empty files
- Remove embedded copies of other libraries, for example libpng embeds zlib.
  - Remove all hashes in libpng that also exist zlib.
- Remove remaining inter-library duplicates, usually stuff like
  - license files
  - standard .gitignore files
  - build system artifacts
  - etc

The result is a database where no hash ever points to more than one library.
Duplicates within a library are kept, though.

If the sparse mode is configured properly, prune() shouldn't find anything.

### Client
The client (`identify.py`) hashes all C/C++ files in a directory and looks up
the respective database entries.

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

```
# ./identify.py cmake-3.29.2
Utilities/cmcurl/lib/http.c curl curl-8_5_0-248-g066ed4e51
Utilities/cmcurl/lib/smtp.c curl curl-8_5_0-216-gc2d973627
Utilities/cmliblzma/liblzma/api/lzma/block.h xz v5.3.1alpha-22-g2fb0ddaa
Utilities/cmliblzma/liblzma/common/block_decoder.c xz v5.2.1-60-gd4a0462a
Utilities/cmliblzma/liblzma/common/block_encoder.c xz v5.2.1-60-gd4a0462a
Utilities/cmliblzma/liblzma/common/stream_decoder.c xz v5.2.1-64-g84462afa
Utilities/cmliblzma/liblzma/common/stream_encoder.c xz v5.2.1-60-gd4a0462a
Utilities/cmliblzma/liblzma/lz/lz_decoder.c xz v5.3.1alpha-48-g608517b9
Utilities/cmliblzma/liblzma/lz/lz_encoder.c xz v5.2.1-60-gd4a0462a
Utilities/cmliblzma/liblzma/lzma/lzma_decoder.c xz v5.3.1alpha-65-g7136f173
Utilities/cmliblzma/liblzma/lzma/lzma_encoder.c xz v5.3.1alpha-65-g7136f173
Utilities/cmliblzma/liblzma/rangecoder/range_decoder.h xz v5.1.1alpha-70-g1403707f
Utilities/cmlibuv/src/uv-common.h libuv v1.44.0-5-gbae2992c
Utilities/cmlibuv/src/unix/linux-core.c libuv v1.43.0-47-gc40f8cb9
Utilities/cmzlib/deflate.h zlib v1.2.12-2-g3df8424
Utilities/cmzlib/gzlib.c zlib v1.2.12-21-g84c6716
Utilities/cmzlib/inflate.c zlib v1.2.12-30-ga9e14e8
Utilities/cmzstd/lib/zstd.h zstd 0^20210512.c730b8c5a38b9e93efc0c3639e26f18f14b82f95
Utilities/cmzstd/lib/common/fse.h zstd 0^20210330.a494308ae9834adea1696564d75c59e66718f4f4
Utilities/cmzstd/lib/common/zstd_internal.h zstd 0^20210409.550f76f1312833c1d1791d22da402bcbb07d5938
Utilities/cmzstd/lib/compress/zstd_compress.c zstd 0^20210507.9e94b7cac5ecccdeb357f7c20decd17992536775
Utilities/cmzstd/lib/decompress/zstd_decompress.c zstd 0^20210426.6cee3c2c4f031125f487d2aa09c878e52a18fd4e
```

In summarize mode (`-s`), it groups the matches by library and shows the
description of the latest match respectively (sorted by git commit timestamp).

```
# ./identify.py -s cmake-3.29.2
curl curl-8_5_0-248-g066ed4e51
xz v5.3.1alpha-65-g7136f173
libuv v1.44.0-5-gbae2992c
zlib v1.2.12-30-ga9e14e8
zstd 0^20210512.c730b8c5a38b9e93efc0c3639e26f18f14b82f95
```

## Adding new libraries
TODO
