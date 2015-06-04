"""
:Authors: Wilker Aziz
"""

import gzip


def smart_open(path, *args, **kwargs):
    """Opens files directly or through gzip depending on extension."""
    if path.endswith('.gz'):
        return gzip.open(path, *args, **kwargs)
    else:
        return open(path, *args, **kwargs)

