from .g2p import G2P
from .prondict import PronDict

__all__ = ['G2P', 'PronDict']

from . import _version
__version__ = _version.get_versions()['version']
