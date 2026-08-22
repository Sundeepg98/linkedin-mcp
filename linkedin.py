#!/usr/bin/env python
"""Entry point for the read-only LinkedIn reader MCP server (stdio transport)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from linkedin_server.server import main

if __name__ == "__main__":
    main()
