"""Pytest conftest for the projects/ subtree.

This file makes each project's `src/` directory available on sys.path so
tests can import the local packages as top-level modules (e.g. `fleet.core`).
"""
import glob
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))

# Add both the project directory (so `import src.*` works) and the project's
# `src/` directory (so `import <pkg>.*` works) to sys.path.
for proj in glob.glob(os.path.join(ROOT, "*")):
    if not os.path.isdir(proj):
        continue
    # project directory (contains `src/`)
    proj_abspath = os.path.abspath(proj)
    if proj_abspath not in sys.path:
        sys.path.insert(0, proj_abspath)
    # project's src directory
    src = os.path.join(proj, "src")
    if os.path.isdir(src):
        src_abspath = os.path.abspath(src)
        if src_abspath not in sys.path:
            sys.path.insert(0, src_abspath)
