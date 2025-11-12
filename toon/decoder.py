"""TOON decoder - convert TOON format to Python objects."""
import re
from typing import Any, Dict, List, Optional, Tuple
from .constants import (
    COMMA, TAB, PIPE, COLON, QUOTE, NEWLINE, SPACE,
    DEFAULT_DELIMITER, DEFAULT_STRICT,
    EXPAND_PATHS_OFF, EXPAND_PATHS_SAFE,
    LEFT_BRACKET, RIGHT_BRACKET, LEFT_BRACE, RIGHT_BRACE
)
from .utils import unescape_string, parse_literal


def detect_indent(toon_string: str) -> int:
    """
    Detect the indentation size used in a TOON string.

    Args:
        toon_string: TOON formatted string

    Returns:
        Detected indent size (default 2 if unable to detect)
    """
    lines = toon_string.split(NEWLINE)

    for line in lines:
        if not line or not line[0].isspace():
            continue

        # Count leading spaces
        indent = 0
        for char in line:
            if char == SPACE:
                indent += 1
            elif char == '\t':
                # Treat tab as 4 spaces
                return 4
            else:
                break

        # If we found indentation, return it
        if indent > 0:
            return indent

    # Default to 2 if no indentation found
    return 2


class DecoderOptions:
    """Options for TOON decoding."""
    
    def __init__(
        self,
        strict: bool = DEFAULT_STRICT,
        expand_paths: str = EXPAND_PATHS_OFF,
        default_delimiter: str = DEFAULT_DELIMITER
    ):
        """
        Initialize decoder options.
        
        Args:
            strict: Validate structure strictly
            expand_paths: Path expansion mode ('off' | 'safe')
            default_delimiter: Default delimiter for arrays
        """
        self.strict = strict
        self.expand_paths = expand_paths
        self.default_delimiter = default_delimiter


def decode(toon_string: str, options: Optional[Dict[str, Any]] = None) -> Any:
    """
    Decode TOON format string to Python data structure.
    
    Args:
        toon_string: TOON formatted string
        options: Decoding options
            - strict: bool (default True) - validate structure
            - expand_paths: 'off' (default) or 'safe'
            - default_delimiter: ',' (default)
            
    Returns:
        Python object (dict or list)
        
    Example:
        >>> toon = '''users[1]{id,name}:
        ...   1,Alice'''
        >>> decode(toon)
        {'users': [{'id': 1, 'name': 'Alice'}]}
    """
    if options is None:
        options = {}

    # Auto-detect indent size unless explicitly provided
    indent_size = options.get('indent')
    if indent_size is None:
        indent_size = detect_indent(toon_string)

    opts = DecoderOptions(
        strict=options.get('strict', DEFAULT_STRICT),
        expand_paths=options.get('expand_paths', EXPAND_PATHS_OFF),
        default_delimiter=options.get('default_delimiter', DEFAULT_DELIMITER)
    )

    lines = toon_string.split(NEWLINE)

    # Handle special case of top-level inline values
    stripped = toon_string.strip()

    # Check if it's an empty object
    if stripped == '{}':
        return {}

    # Check if first line is a root-level array header (tabular or list)
    if lines and lines[0].strip():
        first_line = lines[0].strip()
        # Pattern: [N]{fields}: or [N\t]{fields}: or [N|]{fields}: or [N]:
        array_match = re.match(r'^\[(\d+)([\t|])?\](?:\{([^}]+)\})?' + COLON + r'\s*$', first_line)
        if array_match:
            count = int(array_match.group(1))
            delimiter_indicator = array_match.group(2)
            fields_str = array_match.group(3)

            # Determine delimiter from indicator if present
            if delimiter_indicator == '\t':
                detected_delimiter = TAB
            elif delimiter_indicator == '|':
                detected_delimiter = PIPE
            else:
                detected_delimiter = opts.default_delimiter

            if fields_str:
                # Root-level tabular array
                fields = [f.strip() for f in fields_str.split(COMMA)]
                array_value, _ = _parse_tabular_array(lines, 1, 0, count, fields, opts, detected_delimiter, indent_size)
                return array_value
            else:
                # Root-level list array
                array_value, _ = _parse_list_array(lines, 1, 0, count, opts, indent_size)
                return array_value

    # Check for inline array (must come after array header check)
    if stripped.startswith(LEFT_BRACKET) and stripped.endswith(RIGHT_BRACKET):
        # Top-level inline array
        return _parse_value(stripped, opts)

    result, _ = _parse_lines(lines, 0, 0, opts, indent_size)
    
    # Apply path expansion if enabled
    if opts.expand_paths == EXPAND_PATHS_SAFE and isinstance(result, dict):
        result = _expand_paths(result)
    
    return result


def _parse_lines(lines: List[str], start_idx: int, base_indent: int, opts: DecoderOptions, indent_size: int = 2) -> Tuple[Any, int]:
    """
    Parse lines starting from start_idx with given base indentation.

    Args:
        lines: Lines to parse
        start_idx: Starting line index
        base_indent: Base indentation level
        opts: Decoder options
        indent_size: Size of one indentation level (default 2)

    Returns:
        (parsed_value, next_line_index)
    """
    if start_idx >= len(lines):
        return {}, start_idx
    
    result = {}
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        
        # If indentation is less than base, we're done with this block
        if indent < base_indent:
            break
        
        # If indentation is greater than expected, skip (part of previous value)
        if indent > base_indent:
            i += 1
            continue
        
        # Parse the line
        stripped = line.strip()

        # Check for array header: name[N]{fields}: or name[N\t]{fields}: or name[N|]{fields}:
        # Capture optional delimiter indicator after length
        array_match = re.match(r'^([^:\[\]]+)\[(\d+)([\t|])?\](?:\{([^}]+)\})?' + COLON + r'\s*$', stripped)
        if array_match:
            key = array_match.group(1)
            count = int(array_match.group(2))
            delimiter_indicator = array_match.group(3)
            fields_str = array_match.group(4)

            # Determine delimiter from indicator if present
            if delimiter_indicator == '\t':
                detected_delimiter = TAB
            elif delimiter_indicator == '|':
                detected_delimiter = PIPE
            else:
                detected_delimiter = opts.default_delimiter

            if fields_str:
                # Tabular array
                fields = [f.strip() for f in fields_str.split(COMMA)]
                array_value, i = _parse_tabular_array(lines, i + 1, indent, count, fields, opts, detected_delimiter, indent_size)
            else:
                # List array
                array_value, i = _parse_list_array(lines, i + 1, indent, count, opts, indent_size)

            result[key] = array_value
            continue

        # Check for key-value pair
        if COLON in stripped:
            key, value_str = stripped.split(COLON, 1)
            key = key.strip()
            value_str = value_str.strip()

            if value_str:
                # Inline value
                result[key] = _parse_value(value_str, opts)
                i += 1
            else:
                # Nested value on next lines
                nested_value, i = _parse_lines(lines, i + 1, indent + indent_size, opts, indent_size)
                result[key] = nested_value
        else:
            # No colon - might be a continuation or error
            i += 1
    
    return result, i


def _parse_tabular_array(
    lines: List[str],
    start_idx: int,
    base_indent: int,
    count: int,
    fields: List[str],
    opts: DecoderOptions,
    detected_delimiter: Optional[str] = None,
    indent_size: int = 2
) -> Tuple[List[Dict], int]:
    """Parse a tabular array."""
    result = []
    i = start_idx
    expected_indent = base_indent + indent_size

    # Use provided delimiter from header indicator, or detect from first row
    if detected_delimiter:
        delimiter = detected_delimiter
    else:
        delimiter = opts.default_delimiter
        if i < len(lines):
            first_row = lines[i].strip()
            if TAB in first_row:
                delimiter = TAB
            elif PIPE in first_row:
                delimiter = PIPE
    
    for _ in range(count):
        if i >= len(lines):
            break

        line = lines[i]
        indent = len(line) - len(line.lstrip())

        if indent != expected_indent:
            if opts.strict:
                break
            i += 1
            continue

        # Parse row values
        row_str = line.strip()
        values = _split_row(row_str, delimiter)

        # Create object from fields and values
        obj = {}
        for j, field in enumerate(fields):
            if j < len(values):
                obj[field] = _parse_value(values[j], opts)
            else:
                obj[field] = None

        result.append(obj)
        i += 1

    # Strict mode: validate count matches
    if opts.strict and len(result) != count:
        raise ValueError(f'Array length mismatch: expected {count}, got {len(result)}')

    return result, i


def _parse_list_array(
    lines: List[str],
    start_idx: int,
    base_indent: int,
    count: int,
    opts: DecoderOptions,
    indent_size: int = 2
) -> Tuple[List[Any], int]:
    """Parse a list array."""
    result = []
    i = start_idx
    expected_indent = base_indent + indent_size
    
    for _ in range(count):
        if i >= len(lines):
            break
        
        line = lines[i]
        indent = len(line) - len(line.lstrip())
        
        if indent < expected_indent:
            break
        
        if indent == expected_indent:
            # Check if it's a simple value or nested object
            stripped = line.strip()

            # Strip dash marker if present
            if stripped.startswith('- '):
                stripped = stripped[2:]  # Remove "- " prefix

            if COLON in stripped and not stripped.startswith(LEFT_BRACKET):
                # Nested object - collect all lines for this object
                obj_lines = [' ' * expected_indent + stripped]  # First line without dash
                i += 1

                # Collect subsequent lines that are part of this object (indent > expected_indent)
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())

                    if next_indent <= expected_indent:
                        # Next item or end of array
                        break

                    # Normalize indentation: subtract indent_size spaces to align with first field
                    # Original: '    name: extra field' (4 spaces with indent_size=2)
                    # Becomes:  '  name: extra field' (2 spaces)
                    normalized_line = ' ' * expected_indent + next_line.lstrip()[0:] if next_indent >= expected_indent + indent_size else next_line
                    if next_indent >= expected_indent + indent_size:
                        normalized_line = ' ' * expected_indent + next_line[expected_indent + indent_size:]
                    else:
                        normalized_line = next_line
                    obj_lines.append(normalized_line)
                    i += 1

                # Parse collected lines as an object
                # All lines now have fields at expected_indent
                nested_obj, _ = _parse_lines(obj_lines, 0, expected_indent, opts, indent_size)
                result.append(nested_obj)
            else:
                # Simple value
                result.append(_parse_value(stripped, opts))
                i += 1
        else:
            i += 1

    # Strict mode: validate count matches
    if opts.strict and len(result) != count:
        raise ValueError(f'Array length mismatch: expected {count}, got {len(result)}')

    return result, i


def _split_row(row_str: str, delimiter: str) -> List[str]:
    """
    Split a row by delimiter, respecting quoted strings.
    
    Args:
        row_str: Row string to split
        delimiter: Delimiter character
        
    Returns:
        List of field values
    """
    values = []
    current = []
    in_quote = False
    i = 0
    
    while i < len(row_str):
        char = row_str[i]
        
        if char == QUOTE:
            if in_quote and i + 1 < len(row_str) and row_str[i + 1] == QUOTE:
                # Escaped quote
                current.append(QUOTE)
                i += 2
            else:
                in_quote = not in_quote
                i += 1
        elif char == delimiter and not in_quote:
            values.append(''.join(current))
            current = []
            i += 1
        else:
            current.append(char)
            i += 1
    
    # Add last value
    if current or values:
        values.append(''.join(current))
    
    return values


def _parse_value(value_str: str, opts: DecoderOptions) -> Any:
    """Parse a single value string."""
    value_str = value_str.strip()
    
    if not value_str:
        return None
    
    # Check for quoted string
    if value_str.startswith(QUOTE) and value_str.endswith(QUOTE) and len(value_str) >= 2:
        # Unquote and unescape
        inner = value_str[1:-1]
        return unescape_string(inner)
    
    # Check for inline array [val1,val2,...]
    if value_str.startswith(LEFT_BRACKET) and value_str.endswith(RIGHT_BRACKET):
        inner = value_str[1:-1]
        if not inner:
            return []
        
        # Detect delimiter
        delimiter = COMMA
        if TAB in inner:
            delimiter = TAB
        elif PIPE in inner:
            delimiter = PIPE
        
        values = _split_row(inner, delimiter)
        return [_parse_value(v.strip(), opts) for v in values]
    
    # Check for empty object
    if value_str == '{}':
        return {}
    
    # Parse as literal (bool, null, number, or string)
    return parse_literal(value_str)


def _expand_paths(obj: dict) -> dict:
    """
    Expand dotted paths into nested objects.
    
    Args:
        obj: Object with potentially dotted keys
        
    Returns:
        Expanded object
    """
    result = {}
    
    for key, value in obj.items():
        if '.' in key:
            # Split path and create nested structure
            parts = key.split('.')
            current = result
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Conflict - keep original
                    result[key] = value
                    break
                current = current[part]
            else:
                # Set final value
                current[parts[-1]] = value
        else:
            result[key] = value
    
    # Recursively expand nested objects
    for key, value in result.items():
        if isinstance(value, dict):
            result[key] = _expand_paths(value)
        elif isinstance(value, list):
            result[key] = [_expand_paths(item) if isinstance(item, dict) else item for item in value]
    
    return result
