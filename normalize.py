#!/usr/bin/env python3
"""C/C++ source code normalization."""
import re
import hashlib
from subprocess import Popen, PIPE


def remove_comments(text):
    """Remove comments from C/C++ code"""
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def replacer(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)

    return regex.sub(replacer, text)


def remove_empty_lines(text):
    """Remove duplicate empty lines"""
    return re.sub(r"\n\s*\n", "\n", text, re.MULTILINE)


def clang_format(text, filename):
    """Auto-format C/C++ code with clang.  clang-format recognizes file formats
    by name only, so we need to supply one."""
    p = Popen(["clang-format", "--style=llvm",
               f"--assume-filename={filename}"], stdin=PIPE, stdout=PIPE)
    return p.communicate(input=text.encode("UTF-8"))[0].decode('UTF-8')


def normalized_text(text, filename):
    return clang_format(remove_empty_lines(remove_comments(text)),
                        filename)


def normalized_sha256(text, filename):
    ntext = normalized_text(text, filename)
    m = hashlib.sha256()
    m.update(ntext.encode('UTF-8'))
    return m.hexdigest()


def sha256(filename):
    blob = open(filename, "rb").read()
    m = hashlib.sha256()
    m.update(blob)
    return m.hexdigest()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: normalize.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]

    with open(filename, "r") as f:
        text = f.read()
        print("sha256:           ", sha256(filename))
        print("normalized_sha256:", normalized_sha256(text, filename))


# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
