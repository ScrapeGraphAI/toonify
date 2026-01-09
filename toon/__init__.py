"""TOON (Token-Oriented Object Notation) - A compact serialization format for LLMs."""

from .encoder import encode
from .decoder import decode
from .structure_generator import generate_structure
from .constants import (
    COMMA, TAB, PIPE,
    KEY_FOLDING_OFF, KEY_FOLDING_SAFE,
    EXPAND_PATHS_OFF, EXPAND_PATHS_SAFE
)

# Pydantic converters (optional - requires pydantic installation)
try:
    from .pydantic_converter import encode_pydantic, decode_to_pydantic
    from .structure_generator import generate_structure_from_pydantic
    _PYDANTIC_AVAILABLE = True
except ImportError:
    _PYDANTIC_AVAILABLE = False
    def encode_pydantic(*args, **kwargs):
        raise ImportError("encode_pydantic requires pydantic to be installed. Please install pydantic to use this feature.")
    def decode_to_pydantic(*args, **kwargs):
        raise ImportError("decode_to_pydantic requires pydantic to be installed. Please install pydantic to use this feature.")
    def generate_structure_from_pydantic(*args, **kwargs):
        raise ImportError("generate_structure_from_pydantic requires pydantic to be installed. Please install pydantic to use this feature.")

# Kaggle integration (optional - requires kaggle installation)
try:
    from .kaggle import (
        download_dataset,
        find_best_csv,
        csv_to_records,
        parse_croissant,
        croissant_to_summary,
        is_kaggle_slug,
    )
    _KAGGLE_AVAILABLE = True
except ImportError:
    _KAGGLE_AVAILABLE = False
    def download_dataset(*args, **kwargs):
        raise ImportError("download_dataset requires kaggle to be installed. Please install kaggle to use this feature.")
    def find_best_csv(*args, **kwargs):
        raise ImportError("find_best_csv requires kaggle to be installed. Please install kaggle to use this feature.")
    def csv_to_records(*args, **kwargs):
        raise ImportError("csv_to_records requires kaggle to be installed. Please install kaggle to use this feature.")
    def parse_croissant(*args, **kwargs):
        raise ImportError("parse_croissant requires kaggle to be installed. Please install kaggle to use this feature.")
    def croissant_to_summary(*args, **kwargs):
        raise ImportError("croissant_to_summary requires kaggle to be installed. Please install kaggle to use this feature.")
    def is_kaggle_slug(*args, **kwargs):
        raise ImportError("is_kaggle_slug requires kaggle to be installed. Please install kaggle to use this feature.")

__version__ = '1.0.0'
__all__ = [
    'encode',
    'decode',
    'generate_structure',
    'encode_pydantic',
    'decode_to_pydantic',
    'generate_structure_from_pydantic',
    'download_dataset',
    'find_best_csv',
    'csv_to_records',
    'parse_croissant',
    'croissant_to_summary',
    'is_kaggle_slug',
    'COMMA',
    'TAB',
    'PIPE',
    'KEY_FOLDING_OFF',
    'KEY_FOLDING_SAFE',
    'EXPAND_PATHS_OFF',
    'EXPAND_PATHS_SAFE',
]
