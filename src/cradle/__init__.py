"""cradle: Create repositories with a template structure.

>>> isinstance(__version__, str)
True
"""

import importlib.metadata

__version__ = importlib.metadata.version("rhiza-cradle")
