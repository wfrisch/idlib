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

* sparse mode (default)
* full mode

#### Sparse mode
In sparse mode, only a hand-picked set of files is considered for indexing. The
idea is to improve the signal/noise ratio by choosing files that a) are unique
to the library, b) are unlikely to be omitted in a copy.

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
curl        curl-8_5_0-125-ge556470         Utilities/cmcurl/lib/connect.c
curl        curl-8_5_0-45-g3829759          Utilities/cmcurl/lib/cookie.c
curl        curl-8_5_0-138-gcfe7902         Utilities/cmcurl/lib/easy.c
curl        curl-8_5_0-238-ga6c9a33         Utilities/cmcurl/lib/file.c
curl        curl-8_5_0-45-g3829759          Utilities/cmcurl/lib/formdata.c
curl        curl-8_5_0-40-g907eea0          Utilities/cmcurl/lib/hostip.c
curl        curl-8_5_0-248-g066ed4e         Utilities/cmcurl/lib/http.c
curl        curl-8_5_0-123-ga0f9480         Utilities/cmcurl/lib/http2.c
curl        curl-8_5_0-216-gc2d9736         Utilities/cmcurl/lib/imap.c
curl        curl-8_5_0-167-gd7b6ce6         Utilities/cmcurl/lib/ldap.c
curl        curl-8_5_0-167-gd7b6ce6         Utilities/cmcurl/lib/multi.c
curl        curl-8_5_0-216-gc2d9736         Utilities/cmcurl/lib/pop3.c
curl        curl-8_5_0-182-g3378d2b         Utilities/cmcurl/lib/sendf.c
curl        curl-8_5_0-216-gc2d9736         Utilities/cmcurl/lib/smtp.c
curl        curl-8_5_0-227-g0c05b8f         Utilities/cmcurl/lib/telnet.c
curl        curl-8_5_0-167-gd7b6ce6         Utilities/cmcurl/lib/tftp.c
curl        curl-8_5_0-196-gcdd905a         Utilities/cmcurl/lib/transfer.c
curl        curl-8_5_0-178-gc5801a2         Utilities/cmcurl/lib/url.c
curl        curl-8_5_0-167-gd7b6ce6         Utilities/cmcurl/lib/urldata.h
curl        curl-8_5_0-161-g5d044ad         Utilities/cmcurl/lib/vquic/curl_ngtcp2.c
curl        curl-8_5_0-230-g6d85228         Utilities/cmcurl/lib/vssh/libssh2.c
curl        curl-8_5_0-50-gaf520ac          Utilities/cmcurl/lib/vtls/gtls.c
curl        curl-8_5_0-106-gaff2608         Utilities/cmcurl/lib/vtls/schannel.c
curl        curl-8_5_0-158-gdd0f680         Utilities/cmcurl/lib/vtls/sectransp.c
curl        curl-8_5_0-237-g9a90c9d         Utilities/cmcurl/lib/vtls/vtls.c
libarchive  v3.6.1-39-gd6248d2              Utilities/cmlibarchive/libarchive/archive_entry.c
libarchive  v3.5.2-26-g4b7558e              Utilities/cmlibarchive/libarchive/archive_read.c
libarchive  v3.5.2-26-g2a8bb42              Utilities/cmlibarchive/libarchive/archive_read_disk_entry_from_file.c
libarchive  v3.6.2-47-g2aa73f8              Utilities/cmlibarchive/libarchive/archive_read_disk_windows.c
libarchive  v3.7.0-14-gcc4147e              Utilities/cmlibarchive/libarchive/archive_read_support_format_lha.c
libarchive  v3.6.2-33-ge605604              Utilities/cmlibarchive/libarchive/archive_read_support_format_mtree.c
libarchive  v3.6.1-84-ge2f7c1d              Utilities/cmlibarchive/libarchive/archive_read_support_format_tar.c
libarchive  v3.6.2-7-g0348e24               Utilities/cmlibarchive/libarchive/archive_read_support_format_warc.c
libarchive  v3.6.2-45-g35b79b0              Utilities/cmlibarchive/libarchive/archive_string.c
libarchive  v3.6.2-48-g9e1081b              Utilities/cmlibarchive/libarchive/archive_windows.c
libarchive  v3.6.2-58-g092631c              Utilities/cmlibarchive/libarchive/archive_write_disk_windows.c
libarchive  v3.4.2-11-gfe465c0              Utilities/cmlibarchive/libarchive/archive_write_set_format_mtree.c
libarchive  v3.7.1-9-g1b4e0d0               Utilities/cmlibarchive/libarchive/archive_write_set_format_pax.c
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/ascii.h
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/asciitab.h
libexpat    R_2_4_5-7-g28f7454              Utilities/cmexpat/lib/expat.h
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/iasciitab.h
libexpat    R_2_3_0-88-g5dbc857             Utilities/cmexpat/lib/internal.h
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/latin1tab.h
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/nametab.h
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/utf8tab.h
libexpat    R_2_4_5-7-g28f7454              Utilities/cmexpat/lib/xmlparse.c
libexpat    R_2_4_4-2-g317c917              Utilities/cmexpat/lib/xmlrole.c
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/xmlrole.h
libexpat    R_2_4_4-24-gfdbd69b             Utilities/cmexpat/lib/xmltok.c
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/xmltok.h
libexpat    R_2_4_4-24-gfdbd69b             Utilities/cmexpat/lib/xmltok_impl.c
libexpat    R_2_3_0-55-gdf42f93             Utilities/cmexpat/lib/xmltok_impl.h
libexpat    R_2_4_2-31-g6496a03             Utilities/cmexpat/lib/xmltok_ns.c
libuv       v1.44.0-5-gbae2992              Utilities/cmlibuv/src/uv-common.h
libuv       v1.43.0-47-gc40f8cb             Utilities/cmlibuv/src/unix/linux-core.c
nghttp2     v1.47.0-81-gb0fbb93             Utilities/cmnghttp2/lib/nghttp2_frame.c
nghttp2     v1.47.0-79-gc10a555             Utilities/cmnghttp2/lib/nghttp2_hd.c
nghttp2     v1.49.0-5-geb06e33              Utilities/cmnghttp2/lib/nghttp2_session.c
nghttp2     v1.49.0-5-geb06e33              Utilities/cmnghttp2/lib/nghttp2_session.h
nghttp2     v1.50.0-25-g3f65ab7             Utilities/cmnghttp2/lib/includes/nghttp2/nghttp2.h
xz          v5.2.4-15-g0d31840              Utilities/cmliblzma/liblzma/api/lzma/block.h
xz          v5.3.1alpha-22-g2fb0dda         Utilities/cmliblzma/liblzma/api/lzma/block.h
xz          v5.2.2-33-ge013a33              Utilities/cmliblzma/liblzma/common/block_decoder.c
xz          v5.2.1-60-gd4a0462              Utilities/cmliblzma/liblzma/common/block_decoder.c
xz          v5.2.1-60-gd4a0462              Utilities/cmliblzma/liblzma/common/block_encoder.c
xz          v5.2.2-33-ge013a33              Utilities/cmliblzma/liblzma/common/block_encoder.c
xz          v5.2.3-2-gef36c63               Utilities/cmliblzma/liblzma/common/stream_decoder.c
xz          v5.2.1-64-g84462af              Utilities/cmliblzma/liblzma/common/stream_decoder.c
xz          v5.2.2-33-ge013a33              Utilities/cmliblzma/liblzma/common/stream_encoder.c
xz          v5.2.1-60-gd4a0462              Utilities/cmliblzma/liblzma/common/stream_encoder.c
xz          v5.2.4-37-g0e3c400              Utilities/cmliblzma/liblzma/lz/lz_decoder.c
xz          v5.3.1alpha-48-g608517b         Utilities/cmliblzma/liblzma/lz/lz_decoder.c
xz          v5.2.2-33-ge013a33              Utilities/cmliblzma/liblzma/lz/lz_encoder.c
xz          v5.2.1-60-gd4a0462              Utilities/cmliblzma/liblzma/lz/lz_encoder.c
xz          v5.2.4-50-g00517d1              Utilities/cmliblzma/liblzma/lzma/lzma_decoder.c
xz          v5.3.1alpha-65-g7136f17         Utilities/cmliblzma/liblzma/lzma/lzma_decoder.c
xz          v5.2.4-50-g00517d1              Utilities/cmliblzma/liblzma/lzma/lzma_encoder.c
xz          v5.3.1alpha-65-g7136f17         Utilities/cmliblzma/liblzma/lzma/lzma_encoder.c
xz          v5.1.1alpha-70-g1403707         Utilities/cmliblzma/liblzma/rangecoder/range_decoder.h
zlib        v1.2.9                          Utilities/cmzlib/adler32.c
zlib        v1.2.12-21-g84c6716             Utilities/cmzlib/compress.c
zlib        v1.2.12-31-g888b3da             Utilities/cmzlib/crc32.c
zlib        v1.2.11-38-gf8719f5             Utilities/cmzlib/crc32.h
zlib        v1.2.12-2-g3df8424              Utilities/cmzlib/deflate.h
zlib        v1.2.3.9                        Utilities/cmzlib/gzclose.c
zlib        v1.2.12                         Utilities/cmzlib/gzguts.h
zlib        v1.2.12-21-g84c6716             Utilities/cmzlib/gzlib.c
zlib        v1.2.11-11-g60a5ecc             Utilities/cmzlib/inffast.c
zlib        v1.2.5                          Utilities/cmzlib/inffast.h
zlib        v1.2.5.1-28-g518ad01            Utilities/cmzlib/inffixed.h
zlib        v1.2.12-30-ga9e14e8             Utilities/cmzlib/inflate.c
zlib        v1.2.12                         Utilities/cmzlib/inflate.h
zlib        v1.2.13                         Utilities/cmzlib/inftrees.c
zlib        v1.2.12-14-g5752b17             Utilities/cmzlib/inftrees.h
zlib        v1.2.12-21-g84c6716             Utilities/cmzlib/trees.c
zlib        v1.2.4.5                        Utilities/cmzlib/trees.h
zlib        v1.2.12-21-g84c6716             Utilities/cmzlib/uncompr.c
zlib        v1.2.12-25-gd0704a8             Utilities/cmzlib/zutil.c
zstd        v1.4.7-356-gc730b8c             Utilities/cmzstd/lib/zstd.h
zstd        v1.4.7-226-ga494308             Utilities/cmzstd/lib/common/fse.h
zstd        v1.4.7-197-gde9de86             Utilities/cmzstd/lib/common/fse.h
zstd        v1.4.7-236-g550f76f             Utilities/cmzstd/lib/common/zstd_internal.h
zstd        v1.4.7-334-g9e94b7c             Utilities/cmzstd/lib/compress/zstd_compress.c
zstd        v1.4.7-251-g6cee3c2             Utilities/cmzstd/lib/decompress/zstd_decompress.c
```

In summarize mode (`-s`), it groups the matches by library and shows the
description of the latest match respectively (sorted by git commit timestamp).

```
# ./identify.py -s cmake-3.29.2
curl curl-8_5_0-248-g066ed4e
libarchive v3.7.1-9-g1b4e0d0
libexpat R_2_4_5-7-g28f7454
libuv v1.44.0-5-gbae2992
nghttp2 v1.50.0-25-g3f65ab7
xz v5.2.4-50-g00517d1
zlib v1.2.13
zstd v1.4.7-356-gc730b8c
```

## Adding new libraries
Rough outline
```
cd libraries
git submodule add https://github.com/abc/libxyz
cd ..
./metric.py -n 40 libraries/libxyz/

# add the library definition including the list of sparse files generated by metric.py
$EDITOR config.py

# test the sparse configuration
./index.py -m sparse -d idlib.sqlite -l libxyz

# test the full configuration
# then pay attention to duplicated files:
# libxyz might embed other indexed libraries. adjust config.py accordingly.
./index.py -m full -d idlib-full.sqlite -l libxyz
```
