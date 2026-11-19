#!/usr/bin/env python3
"""news-image-20261118 entrypoint.

Copies the pre-rendered front-page image (entry.png, drawn by draw_news.py
with Pillow) to the grader's output directory as entry.png.

Standard library only, no network, deterministic: the same input bytes are
written on every run, so both grader runs produce identical files.
"""

import hashlib
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"


def fail(message):
    """Print an error and return a non-zero exit code."""
    print("error: " + message, file=sys.stderr)
    return 1


def locate_source():
    """Absolute path of the entry.png shipped beside this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def validate_png(path):
    """Return an error string, or None when the file is a valid entry image.

    Checks the PNG magic bytes and the competition's 1 MiB size limit.
    """
    if not os.path.isfile(path):
        return SOURCE_NAME + " not found next to main.py"
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        return "%s is %d bytes, over the 1048576 byte limit" % (SOURCE_NAME, size)
    with open(path, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        return SOURCE_NAME + " does not start with the PNG magic bytes"
    return None


def output_dir():
    """The grader's output directory: MAKEFUN_OUTPUT_DIR, or /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def run():
    source = locate_source()
    problem = validate_png(source)
    if problem is not None:
        return fail(problem)

    target_dir = output_dir()
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as exc:
        return fail("cannot create output dir %s: %s" % (target_dir, exc))

    target = os.path.join(target_dir, OUTPUT_NAME)
    try:
        shutil.copyfile(source, target)
    except OSError as exc:
        return fail("cannot write %s: %s" % (target, exc))

    # Verify the copy is byte-identical to the shipped image, so a partial
    # write can never pass as a valid entry.
    def digest(path):
        hasher = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    if digest(source) != digest(target):
        return fail("copied file differs from " + SOURCE_NAME)

    print("wrote %s (%d bytes)" % (target, os.path.getsize(target)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
