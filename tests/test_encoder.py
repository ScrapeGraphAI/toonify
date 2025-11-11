"""Tests for TOON encoder."""
import pytest
from toon import encode


def test_encode_primitive_types():
    """Test encoding of primitive types."""
    # String
    assert encode({'name': 'Alice'}) == 'name: Alice'
    
    # Number
    assert encode({'age': 30}) == 'age: 30'
    assert encode({'price': 19.99}) == 'price: 19.99'
    
    # Boolean
    assert encode({'active': True}) == 'active: true'
    assert encode({'disabled': False}) == 'disabled: false'
    
    # Null
    assert encode({'value': None}) == 'value: null'


def test_encode_string_quoting():
    """Test string quoting rules."""
    # Simple string - no quotes
    assert encode({'name': 'Alice'}) == 'name: Alice'
    
    # String with comma - needs quotes
    assert encode({'text': 'Hello, World'}) == 'text: "Hello, World"'
    
    # String with colon - needs quotes
    assert encode({'text': 'key: value'}) == 'text: "key: value"'
    
    # String with leading/trailing space - needs quotes
    assert encode({'text': ' padded '}) == 'text: " padded "'
    
    # String that looks like boolean - needs quotes
    assert encode({'text': 'true'}) == 'text: "true"'
    assert encode({'text': 'false'}) == 'text: "false"'
    
    # String that looks like null - needs quotes
    assert encode({'text': 'null'}) == 'text: "null"'
    
    # Empty string - needs quotes
    assert encode({'text': ''}) == 'text: ""'


def test_encode_string_escaping():
    """Test string escaping."""
    # Quote escaping
    assert encode({'text': 'He said "hello"'}) == 'text: "He said \\"hello\\""'
    
    # Newline escaping
    assert encode({'text': 'line1\nline2'}) == 'text: "line1\\nline2"'
    
    # Backslash escaping
    assert encode({'text': 'path\\to\\file'}) == 'text: "path\\\\to\\\\file"'


def test_encode_empty_structures():
    """Test encoding of empty structures."""
    # Empty object
    assert encode({}) == '{}'
    
    # Empty array
    assert encode({'items': []}) == 'items: []'
    
    # Object with empty array
    data = {'data': {'items': []}}
    result = encode(data)
    assert 'data:' in result
    assert 'items: []' in result


def test_encode_primitive_array():
    """Test encoding of primitive arrays."""
    # Number array
    assert encode({'numbers': [1, 2, 3]}) == 'numbers: [1,2,3]'
    
    # String array
    assert encode({'names': ['Alice', 'Bob']}) == 'names: [Alice,Bob]'
    
    # Mixed primitive array
    assert encode({'mixed': [1, 'text', True, None]}) == 'mixed: [1,text,true,null]'
    
    # Array with quoted strings
    data = {'items': ['hello', 'world, test', 'foo']}
    result = encode(data)
    assert result == 'items: [hello,"world, test",foo]'


def test_encode_array_delimiter():
    """Test different array delimiters."""
    data = {'numbers': [1, 2, 3]}
    
    # Comma (default)
    assert encode(data, {'delimiter': 'comma'}) == 'numbers: [1,2,3]'
    
    # Tab
    result_tab = encode(data, {'delimiter': 'tab'})
    assert result_tab == 'numbers: [1\t2\t3]'
    
    # Pipe
    result_pipe = encode(data, {'delimiter': 'pipe'})
    assert result_pipe == 'numbers: [1|2|3]'


def test_encode_tabular_array():
    """Test encoding of uniform object arrays in tabular format."""
    data = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'}
        ]
    }
    
    result = encode(data)
    lines = result.split('\n')
    
    # Check header
    assert lines[0] == 'users[2]{id,name,role}:'
    
    # Check rows
    assert lines[1] == '  1,Alice,admin'
    assert lines[2] == '  2,Bob,user'


def test_encode_tabular_array_with_tab_delimiter():
    """Test tabular array with tab delimiter."""
    data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    result = encode(data, {'delimiter': 'tab'})
    lines = result.split('\n')

    # Tab delimiter should have \t indicator in header
    assert lines[0] == 'users[2\t]{id,name}:'
    assert lines[1] == '  1\tAlice'
    assert lines[2] == '  2\tBob'


def test_encode_non_uniform_array():
    """Test encoding of non-uniform arrays."""
    data = {
        'items': [
            {'id': 1, 'name': 'Item1'},
            {'id': 2, 'type': 'Special'}
        ]
    }
    
    result = encode(data)
    
    # Should use list format, not tabular
    assert 'items[2]:' in result
    assert '{' not in result  # No field header


def test_encode_nested_objects():
    """Test encoding of nested objects."""
    data = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    result = encode(data)
    lines = result.split('\n')
    
    # Check structure
    assert 'user:' in result
    assert 'name: Alice' in result
    assert 'profile:' in result
    assert 'age: 30' in result
    assert 'city: NYC' in result


def test_encode_key_folding():
    """Test key folding feature."""
    data = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    
    # Without key folding
    result_no_fold = encode(data, {'key_folding': 'off'})
    assert 'data:' in result_no_fold
    assert 'metadata:' in result_no_fold
    
    # With key folding
    result_fold = encode(data, {'key_folding': 'safe'})
    assert 'data.metadata.items' in result_fold


def test_encode_indentation():
    """Test custom indentation."""
    data = {
        'parent': {
            'child': 'value'
        }
    }
    
    # Default indent (2 spaces)
    result_default = encode(data)
    assert '  child: value' in result_default
    
    # Custom indent (4 spaces)
    result_custom = encode(data, {'indent': 4})
    assert '    child: value' in result_custom


def test_encode_special_float_values():
    """Test encoding of special float values (NaN, Infinity)."""
    import math
    
    # NaN
    assert encode({'value': float('nan')}) == 'value: null'
    
    # Infinity
    assert encode({'value': float('inf')}) == 'value: null'
    assert encode({'value': float('-inf')}) == 'value: null'


def test_encode_complex_structure():
    """Test encoding of complex nested structure."""
    data = {
        'project': 'TOON',
        'version': '1.0.0',
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ],
        'metadata': {
            'created': '2024-01-01',
            'tags': ['format', 'serialization', 'llm']
        }
    }
    
    result = encode(data)
    
    # Verify structure exists
    assert 'project: TOON' in result
    assert 'version: 1.0.0' in result
    assert 'users[2]{id,name,active}:' in result
    assert 'metadata:' in result
    assert 'tags: [format,serialization,llm]' in result


def test_encode_tabular_array_with_delimiter_indicator_tab():
    """Test encoding tabular array with tab delimiter shows indicator in header."""
    data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }

    result = encode(data, {'delimiter': 'tab'})
    lines = result.split('\n')

    # Should have tab indicator in header: users[2\t]{id,name}:
    assert lines[0] == 'users[2\t]{id,name}:'
    assert lines[1] == '  1\tAlice'
    assert lines[2] == '  2\tBob'


def test_encode_tabular_array_with_delimiter_indicator_pipe():
    """Test encoding tabular array with pipe delimiter shows indicator in header."""
    data = {
        'products': [
            {'sku': 'A001', 'price': 29.99},
            {'sku': 'B002', 'price': 49.99}
        ]
    }

    result = encode(data, {'delimiter': 'pipe'})
    lines = result.split('\n')

    # Should have pipe indicator in header: products[2|]{sku,price}:
    assert lines[0] == 'products[2|]{sku,price}:'
    assert lines[1] == '  A001|29.99'
    assert lines[2] == '  B002|49.99'


def test_encode_tabular_array_comma_no_indicator():
    """Test encoding tabular array with comma delimiter has no indicator (default)."""
    data = {
        'items': [
            {'code': 'X', 'count': 5},
            {'code': 'Y', 'count': 10}
        ]
    }

    result = encode(data, {'delimiter': 'comma'})
    lines = result.split('\n')

    # Comma is default, no indicator in header
    assert lines[0] == 'items[2]{code,count}:'
    assert lines[1] == '  X,5'
    assert lines[2] == '  Y,10'


def test_encode_list_array_with_dash_markers():
    """Test encoding list array (non-uniform) with dash markers."""
    # Array containing objects/lists (not all primitives) uses list format with dashes
    data = {
        'items': ['apple', {'type': 'fruit'}, 'cherry']
    }

    result = encode(data)
    lines = result.split('\n')

    # Should have dash markers for each item in list format
    assert lines[0] == 'items[3]:'
    assert lines[1] == '  - apple'
    assert lines[2] == '  - type: fruit'
    assert lines[3] == '  - cherry'


def test_encode_mixed_array_with_dash_markers():
    """Test encoding mixed array (objects and primitives) with dash markers."""
    data = {
        'mixed': [
            'string value',
            42,
            {'key': 'value'}
        ]
    }

    result = encode(data)
    lines = result.split('\n')

    # Should have dash markers
    assert lines[0] == 'mixed[3]:'
    assert lines[1] == '  - string value'
    assert lines[2] == '  - 42'
    assert lines[3] == '  - key: value'


def test_encode_datetime_object():
    """Test encoding datetime objects as ISO 8601 strings."""
    from datetime import datetime

    data = {
        'created': datetime(2024, 1, 1, 12, 30, 45),
        'updated': datetime(2024, 6, 15, 9, 0, 0)
    }

    result = encode(data)
    lines = result.split('\n')

    # Datetime should be encoded as quoted ISO strings
    assert lines[0] == 'created: "2024-01-01T12:30:45"'
    assert lines[1] == 'updated: "2024-06-15T09:00:00"'


def test_encode_date_object():
    """Test encoding date objects as ISO 8601 date strings."""
    from datetime import date

    data = {
        'birth_date': date(1990, 5, 20),
        'event_date': date(2024, 12, 25)
    }

    result = encode(data)
    lines = result.split('\n')

    # Date should be encoded as ISO date strings (no quotes needed - no special chars)
    assert lines[0] == 'birth_date: 1990-05-20'
    assert lines[1] == 'event_date: 2024-12-25'


def test_encode_datetime_in_array():
    """Test encoding datetime objects in arrays."""
    from datetime import datetime

    data = {
        'events': [
            {'name': 'Start', 'time': datetime(2024, 1, 1, 0, 0, 0)},
            {'name': 'End', 'time': datetime(2024, 12, 31, 23, 59, 59)}
        ]
    }

    result = encode(data)

    # Should have datetime in tabular format
    assert 'events[2]{name,time}:' in result
    assert 'Start,"2024-01-01T00:00:00"' in result
    assert 'End,"2024-12-31T23:59:59"' in result


def test_encode_float_scientific_notation_suppression():
    """Test that scientific notation is suppressed for reasonable float values."""
    data = {
        'small': 0.000001,  # Would be 1e-06
        'smaller': 0.0000001,  # Would be 1e-07
        'large': 15000000000000000.0,  # Would be 1.5e+16
        'very_large': 1.23e20,  # Scientific notation
        'normal': 3.14159,
        'integer_float': 42.0
    }

    result = encode(data)
    lines = result.split('\n')

    # Check that small numbers are not in scientific notation
    assert 'small: 0.000001' in result
    assert 'smaller: 0.0000001' in result

    # Check that large numbers are not in scientific notation (when reasonable)
    assert 'large: 15000000000000000' in result
    assert 'very_large: 123000000000000000000' in result

    # Check normal floats
    assert 'normal: 3.14159' in result

    # Check integer-valued floats don't have unnecessary decimals
    assert 'integer_float: 42' in result

    # Ensure NO scientific notation (1e, 2e, etc.)
    for line in lines:
        if not line.startswith('#'):  # Skip comments if any
            assert 'e+' not in line.lower()
            assert 'e-' not in line.lower() or 'time' in line.lower()  # Except in words like "time"


def test_encode_float_extreme_values_keep_scientific():
    """Test that extremely large/small values keep scientific notation."""
    data = {
        'very_small': 1.23e-150,
        'very_large': 1.23e150
    }

    result = encode(data)

    # Very extreme values should keep scientific notation
    assert '1.23e-150' in result or '1.23E-150' in result
    assert '1.23e+150' in result or '1.23E+150' in result or '1.23e150' in result


def test_encode_float_array_scientific_notation():
    """Test scientific notation suppression in arrays."""
    data = {
        'values': [0.000001, 0.0000001, 1.5e16, 3.14159, 42.0],
        'tabular': [
            {'id': 1, 'value': 0.000001},
            {'id': 2, 'value': 1.5e16}
        ]
    }

    result = encode(data)

    # Inline array should not have scientific notation
    assert 'values: [0.000001,0.0000001,15000000000000000,3.14159,42]' in result

    # Tabular array should not have scientific notation
    assert '1,0.000001' in result
    assert '2,15000000000000000' in result


def test_encode_root_inline_array():
    """Test encoding root-level inline array."""
    data = [1, 2, 3, 4, 5]

    result = encode(data)

    assert result == '[1,2,3,4,5]'


def test_encode_root_tabular_array():
    """Test encoding root-level tabular array."""
    data = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]

    result = encode(data)

    # Should have tabular format with header
    assert '[3]{id,name}:' in result
    assert '1,Alice' in result
    assert '2,Bob' in result
    assert '3,Charlie' in result


def test_encode_root_list_array():
    """Test encoding root-level list array."""
    data = [
        1,
        'text',
        {'nested': 'object'},
        [1, 2, 3]
    ]

    result = encode(data)

    # Should have list format with dash markers
    assert '[4]:' in result
    assert '- 1' in result
    assert '- text' in result
    assert '- nested: object' in result
    assert '- [1,2,3]' in result
