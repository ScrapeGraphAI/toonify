"""TOON (Token-Oriented Object Notation) - A compact serialization format for LLMs."""

from .encoder import encode
from .decoder import decode
from .constants import (
    COMMA, TAB, PIPE,
    KEY_FOLDING_OFF, KEY_FOLDING_SAFE,
    EXPAND_PATHS_OFF, EXPAND_PATHS_SAFE
)

# Pydantic converters (optional - requires pydantic installation)
try:
    from .pydantic_converter import encode_pydantic, decode_to_pydantic
    _PYDANTIC_AVAILABLE = True
except ImportError:
    _PYDANTIC_AVAILABLE = False
    encode_pydantic = None
    decode_to_pydantic = None

__version__ = '1.0.0'
__all__ = [
    'encode',
    'decode',
    'encode_pydantic',
    'decode_to_pydantic',
    'COMMA',
    'TAB',
    'PIPE',
    'KEY_FOLDING_OFF',
    'KEY_FOLDING_SAFE',
    'EXPAND_PATHS_OFF',
    'EXPAND_PATHS_SAFE',
]
