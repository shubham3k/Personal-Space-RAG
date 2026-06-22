"""Personal Life OS source package."""

import sys

if sys.version_info < (3, 11):
    raise RuntimeError("Personal Life OS requires Python 3.11 or newer.")
