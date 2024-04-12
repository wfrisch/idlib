#!/usr/bin/env python3
from pathlib import Path
import argparse
import collections
import hashlib
import re
import sqlite3
import sys


parser = argparse.ArgumentParser(
        prog="identify.py",
        description="Identify embedded open-source libraries")
parser.add_argument('-d',
                    help="database path. Default: ./idlib.db",
                    default="idlib.db", dest='db')
parser.add_argument("-s", "--summarize", action="store_true", dest="summarize",
                    help="don't report individual files, just the detected "
                    "libs and their most probable version respectively.")
parser.add_argument("--list-libraries", action="store_true",
                    help="list all known libraries")
parser.add_argument("directory",
                    help="directory containing the source code to search")
args = parser.parse_args()
directory = Path(args.directory)


def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = collections.namedtuple("Row", fields)
    return Row(*row)


con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
con.row_factory = namedtuple_factory
cur = con.cursor()


def identify(path):
    blob = open(path, "rb").read()
    m = hashlib.sha256()
    m.update(blob)
    sha256 = m.hexdigest()
    rows = cur.execute("SELECT * FROM files WHERE sha256 = ?", (sha256,))
    return rows


lib_findings = {}  # library name -> database rows

re_cc_filename = re.compile(r'.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$', re.I)
for path in directory.glob('**/*'):
    relpath = path.relative_to(directory)
    if re_cc_filename.match(path.name) and path.is_file():
        rows = identify(path)
        if not args.summarize:
            for row in rows:
                print(relpath, row.library, row.description)
        else:
            for row in rows:
                if row.library not in lib_findings:
                    lib_findings[row.library] = []
                lib_findings[row.library].append(row)
        sys.stdout.flush()

if args.summarize:
    # For each library, sort all matches by the commit time and print only the
    # latest file description.
    for lib_name, rows in lib_findings.items():
        latest = sorted(rows, key=lambda row: row.commit_time)[-1]
        print(lib_name, latest.description)
        sys.stdout.flush()

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
