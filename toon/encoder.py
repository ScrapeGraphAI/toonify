"""TOON encoder - convert Python objects to TOON format."""
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from .constants import (
    COMMA, TAB, PIPE, COLON, NEWLINE,
    DEFAULT_DELIMITER, DEFAULT_INDENT,
    KEY_FOLDING_OFF, KEY_FOLDING_SAFE,
    DELIMITER_TAB, DELIMITER_PIPE, DELIMITER_COMMA,
    LEFT_BRACKET, RIGHT_BRACKET, LEFT_BRACE, RIGHT_BRACE
)
from .utils import (
    needs_quoting, quote_string, is_primitive,
    is_uniform_array_of_objects, get_indent, format_float
)


class EncoderOptions:
    """Options for TOON encoding."""
    
    def __init__(
        self,
        delimiter: str = DEFAULT_DELIMITER,
        indent: int = DEFAULT_INDENT,
        key_folding: str = KEY_FOLDING_OFF,
        flatten_depth: Optional[int] = None
    ):
        """
        Initialize encoder options.
        
        Args:
            delimiter: Array value delimiter (',' | '\t' | '|')
            indent: Number of spaces per indentation level
            key_folding: Key folding mode ('off' | 'safe')
            flatten_depth: Maximum depth for key folding (None = unlimited)
        """
        # Normalize delimiter names
        if delimiter == DELIMITER_TAB:
            delimiter = TAB
        elif delimiter == DELIMITER_PIPE:
            delimiter = PIPE
        elif delimiter == DELIMITER_COMMA:
            delimiter = COMMA
        
        self.delimiter = delimiter
        self.indent = indent
        self.key_folding = key_folding
        self.flatten_depth = flatten_depth


def encode(data: Any, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Encode Python data structure to TOON format.
    
    Args:
        data: Python object to encode (dict or list)
        options: Encoding options
            - delimiter: ',' (default), '\t', or '|'
            - indent: int (default 2)
            - key_folding: 'off' (default) or 'safe'
            - flatten_depth: int or None
            
    Returns:
        TOON formatted string
        
    Example:
        >>> data = {'users': [{'id': 1, 'name': 'Alice'}]}
        >>> print(encode(data))
        users[1]{id,name}:
          1,Alice
    """
    if options is None:
        options = {}
    
    opts = EncoderOptions(
        delimiter=options.get('delimiter', DEFAULT_DELIMITER),
        indent=options.get('indent', DEFAULT_INDENT),
        key_folding=options.get('key_folding', KEY_FOLDING_OFF),
        flatten_depth=options.get('flatten_depth')
    )
    
    return _encode_value(data, 0, opts)


def _encode_value(value: Any, level: int, opts: EncoderOptions) -> str:
    """Encode a value at a given indentation level."""
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, datetime):
        # Convert datetime to ISO 8601 string
        iso_string = value.isoformat()
        if needs_quoting(iso_string):
            return quote_string(iso_string)
        return iso_string
    elif isinstance(value, date):
        # Convert date to ISO 8601 date string
        iso_string = value.isoformat()
        if needs_quoting(iso_string):
            return quote_string(iso_string)
        return iso_string
    elif isinstance(value, (int, float)):
        # Handle special float values
        if isinstance(value, float):
            if value != value:  # NaN
                return 'null'
            elif value == float('inf') or value == float('-inf'):
                return 'null'
            # Use format_float to suppress scientific notation
            return format_float(value)
        return str(value)
    elif isinstance(value, str):
        if needs_quoting(value):
            return quote_string(value)
        return value
    elif isinstance(value, list):
        return _encode_array(value, level, opts)
    elif isinstance(value, dict):
        return _encode_object(value, level, opts)
    else:
        # Handle other types as null
        return 'null'


def _encode_object(obj: dict, level: int, opts: EncoderOptions) -> str:
    """Encode a dictionary object."""
    if not obj:
        return '{}'
    
    # Apply key folding if enabled
    if opts.key_folding == KEY_FOLDING_SAFE:
        obj = _apply_key_folding(obj, opts.flatten_depth)
    
    lines = []
    indent = get_indent(level, opts.indent)
    
    for key, value in obj.items():
        # Special handling for arrays to include key in header
        if isinstance(value, list):
            encoded_value = _encode_array_with_key(key, value, level, opts)
            if NEWLINE in encoded_value:
                lines.append(encoded_value)
            else:
                lines.append(f'{indent}{key}{COLON} {encoded_value}')
        elif isinstance(value, dict):
            # Nested object handling
            if not value:
                # Empty object - inline
                lines.append(f'{indent}{key}{COLON} {{}}')
            else:
                # Non-empty object - multiline
                encoded_value = _encode_value(value, level + 1, opts)
                lines.append(f'{indent}{key}{COLON}')
                lines.append(encoded_value)
        else:
            # Primitive value
            encoded_value = _encode_value(value, level + 1, opts)
            lines.append(f'{indent}{key}{COLON} {encoded_value}')
    
    return NEWLINE.join(lines)


def _encode_array(arr: list, level: int, opts: EncoderOptions) -> str:
    """Encode an array."""
    if not arr:
        return '[]'
    
    # Check if it's a uniform array of objects (tabular format)
    fields = is_uniform_array_of_objects(arr)
    if fields:
        return _encode_tabular_array(arr, fields, level, opts, key=None)
    
    # Check if all elements are primitives (inline format)
    if all(is_primitive(item) for item in arr):
        return _encode_primitive_array(arr, opts)
    
    # Mixed array (list format)
    return _encode_list_array(arr, level, opts, key=None)


def _encode_array_with_key(key: str, arr: list, level: int, opts: EncoderOptions) -> str:
    """Encode an array with its key prefix for object context."""
    if not arr:
        return '[]'
    
    indent = get_indent(level, opts.indent)
    
    # Check if it's a uniform array of objects (tabular format)
    fields = is_uniform_array_of_objects(arr)
    if fields:
        return _encode_tabular_array(arr, fields, level, opts, key=key)
    
    # Check if all elements are primitives (inline format)
    if all(is_primitive(item) for item in arr):
        return _encode_primitive_array(arr, opts)
    
    # Mixed array (list format)
    return _encode_list_array(arr, level, opts, key=key)



def _encode_primitive_array(arr: list, opts: EncoderOptions) -> str:
    """Encode an array of primitives as inline values."""
    encoded_values = []
    for item in arr:
        if item is None:
            encoded_values.append('null')
        elif isinstance(item, bool):
            encoded_values.append('true' if item else 'false')
        elif isinstance(item, (int, float)):
            if isinstance(item, float):
                if item != item or item == float('inf') or item == float('-inf'):
                    encoded_values.append('null')
                else:
                    # Use format_float to suppress scientific notation
                    encoded_values.append(format_float(item))
            else:
                encoded_values.append(str(item))
        elif isinstance(item, str):
            if needs_quoting(item):
                encoded_values.append(quote_string(item))
            else:
                encoded_values.append(item)

    return f'[{opts.delimiter.join(encoded_values)}]'


def _encode_tabular_array(arr: list, fields: list, level: int, opts: EncoderOptions, key: Optional[str] = None) -> str:
    """Encode a uniform array of objects in tabular format."""
    indent = get_indent(level, opts.indent)

    # Delimiter indicator: show delimiter in header for non-comma
    delimiter_indicator = ''
    if opts.delimiter == TAB:
        delimiter_indicator = '\t'
    elif opts.delimiter == PIPE:
        delimiter_indicator = '|'
    # Comma is default, no indicator needed

    # Header: [N]{field1,field2,...}: or key[N\t]{field1,field2,...}: or key[N|]{field1,field2,...}:
    if key:
        header = f'{indent}{key}[{len(arr)}{delimiter_indicator}]{LEFT_BRACE}{COMMA.join(fields)}{RIGHT_BRACE}{COLON}'
    else:
        header = f'[{len(arr)}{delimiter_indicator}]{LEFT_BRACE}{COMMA.join(fields)}{RIGHT_BRACE}{COLON}'
    
    lines = [header]
    
    # Rows: indented values separated by delimiter
    for obj in arr:
        row_values = []
        for field in fields:
            value = obj.get(field)
            encoded = _encode_primitive_value(value)
            row_values.append(encoded)
        
        row = opts.delimiter.join(row_values)
        lines.append(f'{indent}  {row}')
    
    return NEWLINE.join(lines)


def _encode_primitive_value(value: Any) -> str:
    """Encode a primitive value for use in arrays."""
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, datetime):
        # Convert datetime to ISO 8601 string
        iso_string = value.isoformat()
        if needs_quoting(iso_string):
            return quote_string(iso_string)
        return iso_string
    elif isinstance(value, date):
        # Convert date to ISO 8601 date string
        iso_string = value.isoformat()
        if needs_quoting(iso_string):
            return quote_string(iso_string)
        return iso_string
    elif isinstance(value, (int, float)):
        if isinstance(value, float):
            if value != value or value == float('inf') or value == float('-inf'):
                return 'null'
            # Use format_float to suppress scientific notation
            return format_float(value)
        return str(value)
    elif isinstance(value, str):
        if needs_quoting(value):
            return quote_string(value)
        return value
    else:
        return 'null'


def _encode_list_array(arr: list, level: int, opts: EncoderOptions, key: Optional[str] = None) -> str:
    """Encode a non-uniform array in list format."""
    indent = get_indent(level, opts.indent)

    # Header: [N]: or key[N]:
    if key:
        header = f'{indent}{key}[{len(arr)}]{COLON}'
    else:
        header = f'[{len(arr)}]{COLON}'

    lines = [header]

    # Items: indented encoded values with dash markers
    for item in arr:
        if isinstance(item, dict) and item:
            # Nested object: encode at level + 2 for proper subsequent line indentation
            encoded = _encode_value(item, level + 2, opts)
            encoded_lines = encoded.split(NEWLINE)
            # First line: strip leading indent and add dash
            first_line = encoded_lines[0].lstrip()
            lines.append(f'{indent}  - {first_line}')
            # Subsequent lines: keep as-is (already properly indented)
            for line in encoded_lines[1:]:
                lines.append(line)
        else:
            # Simple value: encode and add dash marker
            encoded = _encode_value(item, level + 1, opts)
            lines.append(f'{indent}  - {encoded}')
    
    return NEWLINE.join(lines)


def _apply_key_folding(obj: dict, max_depth: Optional[int] = None) -> dict:
    """
    Apply key folding to collapse single-key chains into dotted paths.
    
    Args:
        obj: Object to fold
        max_depth: Maximum depth for folding (None = unlimited)
        
    Returns:
        Folded object
    """
    result = {}
    
    for key, value in obj.items():
        if isinstance(value, dict) and len(value) == 1:
            # Single-key object - check if we can fold
            nested_key = list(value.keys())[0]
            nested_value = value[nested_key]
            
            # Calculate current depth
            depth = 1
            current = nested_value
            while isinstance(current, dict) and len(current) == 1 and (max_depth is None or depth < max_depth):
                depth += 1
                current = list(current.values())[0]
            
            # Fold if within depth limit
            if max_depth is None or depth <= max_depth:
                folded_key = f'{key}.{nested_key}'
                # Recursively fold
                if isinstance(nested_value, dict) and len(nested_value) == 1:
                    folded = _apply_key_folding({nested_key: nested_value}, max_depth)
                    for fk, fv in folded.items():
                        result[f'{key}.{fk}'] = fv
                else:
                    result[folded_key] = nested_value
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result
