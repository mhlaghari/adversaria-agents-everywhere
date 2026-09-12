"""Run the terminal app: python -m adversaria_terminal."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())