#!/usr/bin/env python3
"""
Run the cancer-genomics teaching app from the research folder.

@author: Preston Mackert
"""

# ------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------- #

from __future__ import annotations
import sys
from pathlib import Path
from app.server import main


# ------------------------------------------------------------------------------------- #
# the apps entry point when python launch.py is executed from the command line
# ------------------------------------------------------------------------------------- #

# ensure root directory is defined
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# https://www.youtube.com/watch?v=hE8nC73dShs
if __name__ == "__main__":
    main()
