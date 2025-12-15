"""Top-level package for Cluster Health Monitor.

Expose high-level package metadata and commonly-used helpers so callers
can import from ``monitor`` conveniently. Keep this file minimal to avoid
heavy import costs at package import time.
"""

__all__ = [
	'__version__',
]

# Package version — keep in sync with distribution metadata
__version__ = '1.2.0'
