"""API package for the monitor web dashboard.

Re-export the primary application factory and common module-level
constants so callers can do::

	from monitor.api import create_app

Keep this file small to avoid importing heavy web framework code at
package import time.
"""

from .server import create_app, TEMPLATE_DIR, STATIC_DIR

__all__ = [
	'create_app',
	'TEMPLATE_DIR',
	'STATIC_DIR',
]
