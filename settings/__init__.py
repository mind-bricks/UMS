import sys

print("Trying import base.py settings...", file=sys.stderr)
from .base import *  # noqa: F401, F403

try:
    from .local import *  # noqa: F401, F403

    # generally speaking, the settings in local.py will not be
    # same with base.py, but if setting in local.py is same with base.py,
    # then it will override.
    print("Trying import local.py settings...", file=sys.stderr)

except ImportError:
    pass
