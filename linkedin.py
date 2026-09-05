#!/usr/bin/env python
"""Entry point for the LinkedIn MCP server.

Two transports, and the default is unchanged:

    python linkedin.py           -> stdio (what .mcp.json has always run)
    python linkedin.py --http    -> streamable HTTP on 127.0.0.1:8322/mcp

The stdio path is byte-for-byte the behaviour it had before ``--http`` was
added, which is what makes the rollback free: put the old two-line command
back in .mcp.json and nothing else has to be undone.

WHY THE SECOND ONE EXISTS. Under stdio the MCP client owns this process, so
loading changed code needs the operator to type ``/mcp``. An HTTP server is
reconnected by the client on its own, so it can be restarted from a shell.
See ``linkedin_server/transport.py`` for the full argument, the safety deltas
that come with a loopback port, and why HTTP wants ``LINKEDIN_CDP_ATTACH=1``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from linkedin_server.server import main, mcp
from linkedin_server.transport import serve_http

if __name__ == "__main__":
    if "--http" in sys.argv[1:]:
        serve_http(mcp)
    else:
        main()
