from .g2p import G2P
from .prondict import PronDict

__all__ = ['G2P', 'PronDict']


__import__('pkg_resources').declare_namespace(__name__)
