"""Utility functions for the TOON library."""
from typing import Any, Optional
from datetime import datetime, date
from .constants import (
    QUOTE, BACKSLASH, NEWLINE, COMMA, TAB, PIPE,
    TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL,
    SPACE, COLON
)


def needs_quoting(value: str) -> bool:
    """
    Check if a string value needs to be quoted.
    
    Quoting is needed when:
    - Value contains special characters (comma, colon, newline, quotes)
    - Value has leading or trailing whitespace
    - Value looks like a boolean or null literal
    - Value is empty
    
    Args:
        value: String to check
        
    Returns:
        True if quoting is needed, False otherwise
    """
    if not value:
        return True
    
    # Check for leading/trailing whitespace
    if value != value.strip():
        return True
    
    # Check if it looks like a literal
    lower_value = value.lower()
    if lower_value in (TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL):
        return True
    
    # Check for special characters
    special_chars = {COMMA, COLON, NEWLINE, QUOTE, TAB, PIPE, BACKSLASH, '[', ']', '{', '}'}
    if any(char in value for char in special_chars):
        return True
    
    # Check if it looks like a number but has trailing content
    # This handles cases like "123abc" which should be quoted
    try:
        float(value)
        return False
    except ValueError:
        pass
    
    return False


def escape_string(value: str) -> str:
    """
    Escape special characters in a string for TOON encoding.
    
    Args:
        value: String to escape
        
    Returns:
        Escaped string
    """
    # Escape backslashes first
    value = value.replace(BACKSLASH, BACKSLASH + BACKSLASH)
    # Escape quotes
    value = value.replace(QUOTE, BACKSLASH + QUOTE)
    # Escape newlines
    value = value.replace(NEWLINE, BACKSLASH + 'n')
    # Escape tabs
    value = value.replace('\t', BACKSLASH + 't')
    # Escape carriage returns
    value = value.replace('\r', BACKSLASH + 'r')
    return value


def unescape_string(value: str) -> str:
    """
    Unescape special characters in a TOON string.
    
    Args:
        value: Escaped string
        
    Returns:
        Unescaped string
    """
    result = []
    i = 0
    while i < len(value):
        if value[i] == BACKSLASH and i + 1 < len(value):
            next_char = value[i + 1]
            if next_char == 'n':
                result.append(NEWLINE)
                i += 2
            elif next_char == 't':
                result.append('\t')
                i += 2
            elif next_char == 'r':
                result.append('\r')
                i += 2
            elif next_char == QUOTE:
                result.append(QUOTE)
                i += 2
            elif next_char == BACKSLASH:
                result.append(BACKSLASH)
                i += 2
            else:
                result.append(value[i])
                i += 1
        else:
            result.append(value[i])
            i += 1
    return ''.join(result)


def quote_string(value: str) -> str:
    """
    Quote and escape a string for TOON encoding.
    
    Args:
        value: String to quote
        
    Returns:
        Quoted and escaped string
    """
    escaped = escape_string(value)
    return f'{QUOTE}{escaped}{QUOTE}'


def is_primitive(value: Any) -> bool:
    """
    Check if a value is a primitive type (str, int, float, bool, None, datetime, date).

    Args:
        value: Value to check

    Returns:
        True if primitive, False otherwise
    """
    return isinstance(value, (str, int, float, bool, type(None), datetime, date))


def is_array_of_objects(value: Any) -> bool:
    """
    Check if a value is an array of objects (list of dicts).
    
    Args:
        value: Value to check
        
    Returns:
        True if array of objects, False otherwise
    """
    if not isinstance(value, list) or not value:
        return False
    return all(isinstance(item, dict) for item in value)


def is_uniform_array_of_objects(value: list) -> Optional[list]:
    """
    Check if an array contains objects with identical primitive fields.
    
    Args:
        value: Array to check
        
    Returns:
        List of field names if uniform, None otherwise
    """
    if not value or not all(isinstance(item, dict) for item in value):
        return None
    
    # Get fields from first object
    first_obj = value[0]
    fields = []
    
    for key, val in first_obj.items():
        if is_primitive(val):
            fields.append(key)
    
    if not fields:
        return None
    
    # Check all objects have the same primitive fields
    for obj in value[1:]:
        obj_fields = [k for k, v in obj.items() if is_primitive(v)]
        if set(obj_fields) != set(fields):
            return None
    
    return fields


def get_indent(level: int, indent_size: int = 2) -> str:
    """
    Get indentation string for a given level.
    
    Args:
        level: Indentation level
        indent_size: Number of spaces per level
        
    Returns:
        Indentation string
    """
    return SPACE * (level * indent_size)


def parse_number(value: str) -> Any:
    """
    Parse a string as a number (int or float).
    
    Args:
        value: String to parse
        
    Returns:
        Parsed number or original string if not a number
    """
    try:
        # Try integer first
        if '.' not in value and 'e' not in value.lower():
            return int(value)
        # Try float
        return float(value)
    except ValueError:
        return value


def parse_literal(value: str) -> Any:
    """
    Parse a string as a boolean, null, or number literal.

    Args:
        value: String to parse

    Returns:
        Parsed value or original string if not a literal
    """
    lower_value = value.lower()
    if lower_value == TRUE_LITERAL:
        return True
    elif lower_value == FALSE_LITERAL:
        return False
    elif lower_value == NULL_LITERAL:
        return None
    else:
        return parse_number(value)


def format_float(value: float) -> str:
    """
    Format a float without unnecessary scientific notation.

    Suppresses scientific notation for numbers in a reasonable range,
    making the output more human-readable.

    Args:
        value: Float value to format

    Returns:
        Formatted string representation
    """
    if value == 0:
        return '0'

    # Check if value would use scientific notation
    str_repr = str(value)
    if 'e' not in str_repr.lower():
        # Already in decimal format, but strip unnecessary trailing zeros
        if '.' in str_repr:
            return str_repr.rstrip('0').rstrip('.')
        return str_repr

    abs_val = abs(value)

    # Only suppress scientific notation for reasonable ranges
    # Keep scientific notation for very large or very small numbers
    if abs_val < 1e-100 or abs_val >= 1e100:
        return str_repr

    # Format with fixed-point notation
    # Use enough precision to preserve the value
    if abs_val >= 1:
        # For numbers >= 1, use minimal decimal places
        formatted = f'{value:.10f}'
    else:
        # For numbers < 1, use more precision
        formatted = f'{value:.15f}'

    # Strip trailing zeros and unnecessary decimal point
    formatted = formatted.rstrip('0').rstrip('.')

    return formatted
