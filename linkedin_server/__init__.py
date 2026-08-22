"""linkedin: a strictly read-only MCP window onto the operator's own LinkedIn.

Reads his profile views, applications, saved jobs, job search, profile and
notifications through his own signed-in browser. There is no write path in
this package -- see ``readonly.py`` for the machinery that keeps that true.
"""

from linkedin_server.config import SERVER_NAME, SERVER_VERSION

__all__ = ["SERVER_NAME", "SERVER_VERSION", "__version__"]
__version__ = SERVER_VERSION
