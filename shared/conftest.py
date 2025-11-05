"""Pytest conftest for the shared/ subtree.

Expose the local `src/` directory (as `src`) on sys.path so tests can import
`src.app` and `src.api` modules.
"""
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))

# Add the shared project directory so `import src.app` resolves to shared/src/app
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
