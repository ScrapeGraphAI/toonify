"""Tests for TOON decoder."""
import pytest
from toon import decode


def test_decode_primitive_types():
    """Test decoding of primitive types."""
    # String
    assert decode('name: Alice') == {'name': 'Alice'}
    
    # Number
    assert decode('age: 30') == {'age': 30}
    assert decode('price: 19.99') == {'price': 19.99}
    
    # Boolean
    assert decode('active: true') == {'active': True}
    assert decode('disabled: false') == {'disabled': False}
    
    # Null
    assert decode('value: null') == {'value': None}


def test_decode_quoted_strings():
    """Test decoding of quoted strings."""
    # Simple quoted string
    assert decode('name: "Alice"') == {'name': 'Alice'}
    
    # String with comma
    assert decode('text: "Hello, World"') == {'text': 'Hello, World'}
    
    # String with colon
    assert decode('text: "key: value"') == {'text': 'key: value'}
    
    # String with spaces
    assert decode('text: " padded "') == {'text': ' padded '}
    
    # Empty string
    assert decode('text: ""') == {'text': ''}


def test_decode_escaped_strings():
    """Test decoding of escaped strings."""
    # Escaped quotes
    assert decode('text: "He said \\"hello\\""') == {'text': 'He said "hello"'}
    
    # Escaped newline
    assert decode('text: "line1\\nline2"') == {'text': 'line1\nline2'}
    
    # Escaped backslash
    assert decode('text: "path\\\\to\\\\file"') == {'text': 'path\\to\\file'}
    
    # Escaped tab
    assert decode('text: "col1\\tcol2"') == {'text': 'col1\tcol2'}


def test_decode_empty_structures():
    """Test decoding of empty structures."""
    # Empty object
    result = decode('data: {}')
    assert result == {'data': {}}
    
    # Empty array
    assert decode('items: []') == {'items': []}


def test_decode_primitive_array():
    """Test decoding of primitive arrays."""
    # Number array
    assert decode('numbers: [1,2,3]') == {'numbers': [1, 2, 3]}
    
    # String array
    assert decode('names: [Alice,Bob]') == {'names': ['Alice', 'Bob']}
    
    # Mixed array
    assert decode('mixed: [1,text,true,null]') == {'mixed': [1, 'text', True, None]}
    
    # Array with quoted strings
    result = decode('items: [hello,"world, test",foo]')
    assert result == {'items': ['hello', 'world, test', 'foo']}


def test_decode_array_delimiters():
    """Test decoding with different delimiters."""
    # Tab delimiter
    assert decode('numbers: [1\t2\t3]') == {'numbers': [1, 2, 3]}
    
    # Pipe delimiter
    assert decode('numbers: [1|2|3]') == {'numbers': [1, 2, 3]}


def test_decode_tabular_array():
    """Test decoding of tabular arrays."""
    toon = """users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user"""
    
    result = decode(toon)
    
    expected = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'}
        ]
    }
    
    assert result == expected


def test_decode_tabular_array_with_tab():
    """Test decoding tabular array with tab delimiter."""
    # Tab delimiter should have \t indicator in header
    toon = """users[2\t]{id,name}:
  1\tAlice
  2\tBob"""

    result = decode(toon)
    
    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    assert result == expected


def test_decode_list_array():
    """Test decoding of list arrays."""
    toon = """items[3]:
  value1
  value2
  value3"""
    
    result = decode(toon)
    assert result == {'items': ['value1', 'value2', 'value3']}


def test_decode_nested_objects():
    """Test decoding of nested objects."""
    toon = """user:
  name: Alice
  profile:
    age: 30
    city: NYC"""
    
    result = decode(toon)
    
    expected = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    assert result == expected


def test_decode_path_expansion():
    """Test path expansion feature."""
    toon = 'data.metadata.items: [1,2,3]'
    
    # Without expansion
    result_no_expand = decode(toon, {'expand_paths': 'off'})
    assert result_no_expand == {'data.metadata.items': [1, 2, 3]}
    
    # With expansion
    result_expand = decode(toon, {'expand_paths': 'safe'})
    expected = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    assert result_expand == expected


def test_decode_complex_structure():
    """Test decoding of complex structure."""
    toon = """project: TOON
version: 1.0.0
users[2]{id,name,active}:
  1,Alice,true
  2,Bob,false
metadata:
  created: 2024-01-01
  tags: [format,serialization,llm]"""
    
    result = decode(toon)
    
    expected = {
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
    
    assert result == expected


def test_decode_empty_lines():
    """Test decoding with empty lines."""
    toon = """name: Alice

age: 30

active: true"""
    
    result = decode(toon)
    assert result == {'name': 'Alice', 'age': 30, 'active': True}


def test_decode_number_formats():
    """Test decoding various number formats."""
    toon = """int: 42
float: 3.14
negative: -10
scientific: 1.5e10"""
    
    result = decode(toon)
    
    assert result['int'] == 42
    assert result['float'] == 3.14
    assert result['negative'] == -10
    assert result['scientific'] == 1.5e10


def test_decode_quoted_field_values():
    """Test decoding with quoted values in tabular arrays."""
    toon = """items[2]{id,description}:
  1,"Item with, comma"
  2,"Normal item\""""
    
    result = decode(toon)
    
    expected = {
        'items': [
            {'id': 1, 'description': 'Item with, comma'},
            {'id': 2, 'description': 'Normal item'}
        ]
    }

    assert result == expected


def test_decode_tabular_array_with_tab_indicator():
    """Test decoding tabular array with tab delimiter indicator in header."""
    toon = """users[2\t]{id,name}:
  1\tAlice
  2\tBob"""

    result = decode(toon)

    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }

    assert result == expected


def test_decode_tabular_array_with_pipe_indicator():
    """Test decoding tabular array with pipe delimiter indicator in header."""
    toon = """products[2|]{sku,price}:
  A001|29.99
  B002|49.99"""

    result = decode(toon)

    expected = {
        'products': [
            {'sku': 'A001', 'price': 29.99},
            {'sku': 'B002', 'price': 49.99}
        ]
    }

    assert result == expected


def test_decode_tabular_array_comma_no_indicator():
    """Test decoding tabular array without delimiter indicator uses comma default."""
    toon = """items[2]{code,count}:
  X,5
  Y,10"""

    result = decode(toon)

    expected = {
        'items': [
            {'code': 'X', 'count': 5},
            {'code': 'Y', 'count': 10}
        ]
    }

    assert result == expected


def test_decode_list_array_with_dash_markers():
    """Test decoding list array with dash markers."""
    toon = """items[3]:
  - apple
  - banana
  - cherry"""

    result = decode(toon)

    expected = {
        'items': ['apple', 'banana', 'cherry']
    }

    assert result == expected


def test_decode_mixed_types_with_dash_markers():
    """Test decoding mixed types array with dash markers."""
    toon = """mixed[3]:
  - string value
  - 42
  - key: value"""

    result = decode(toon)

    expected = {
        'mixed': ['string value', 42, {'key': 'value'}]
    }

    assert result == expected


def test_decode_datetime_string():
    """Test decoding datetime ISO strings."""
    toon = """created: "2024-01-01T12:30:45"
updated: "2024-06-15T09:00:00\""""

    result = decode(toon)

    expected = {
        'created': '2024-01-01T12:30:45',
        'updated': '2024-06-15T09:00:00'
    }

    assert result == expected


def test_decode_scientific_notation():
    """Test decoding numbers in scientific notation."""
    toon = """small: 1e-06
smaller: 1e-07
large: 1.5e+16
very_large: 1.23e20
normal: 3.14159"""

    result = decode(toon)

    expected = {
        'small': 1e-06,
        'smaller': 1e-07,
        'large': 1.5e+16,
        'very_large': 1.23e20,
        'normal': 3.14159
    }

    assert result == expected


def test_decode_decimal_notation():
    """Test decoding numbers in decimal notation (no scientific)."""
    toon = """small: 0.000001
smaller: 0.0000001
large: 15000000000000000
normal: 3.14159
integer: 42"""

    result = decode(toon)

    expected = {
        'small': 0.000001,
        'smaller': 0.0000001,
        'large': 15000000000000000.0,
        'normal': 3.14159,
        'integer': 42
    }

    assert result == expected


def test_decode_float_array_with_scientific():
    """Test decoding arrays with scientific notation numbers."""
    toon = """values: [1e-06,1e-07,1.5e+16,3.14159]"""

    result = decode(toon)

    expected = {
        'values': [1e-06, 1e-07, 1.5e+16, 3.14159]
    }

    assert result == expected


def test_decode_root_inline_array():
    """Test decoding root-level inline array."""
    toon = "[1,2,3,4,5]"

    result = decode(toon)

    expected = [1, 2, 3, 4, 5]

    assert result == expected


def test_decode_root_tabular_array():
    """Test decoding root-level tabular array."""
    toon = """[3]{id,name}:
  1,Alice
  2,Bob
  3,Charlie"""

    result = decode(toon)

    expected = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]

    assert result == expected


def test_decode_root_list_array():
    """Test decoding root-level list array."""
    toon = """[4]:
  - 1
  - text
  - nested: object
  - [1,2,3]"""

    result = decode(toon)

    expected = [
        1,
        'text',
        {'nested': 'object'},
        [1, 2, 3]
    ]

    assert result == expected


def test_decode_4space_indent():
    """Test auto-detecting 4-space indentation."""
    toon = """user:
    name: Alice
    age: 30
    profile:
        city: NYC
        country: USA"""

    result = decode(toon)

    expected = {
        'user': {
            'name': 'Alice',
            'age': 30,
            'profile': {
                'city': 'NYC',
                'country': 'USA'
            }
        }
    }

    assert result == expected


def test_decode_explicit_indent_override():
    """Test explicitly specifying indent size."""
    # 3-space indent (unusual but should work with explicit option)
    toon = """data:
   value: 123
   nested:
      item: test"""

    result = decode(toon, {'indent': 3})

    expected = {
        'data': {
            'value': 123,
            'nested': {
                'item': 'test'
            }
        }
    }

    assert result == expected


def test_decode_array_with_custom_indent():
    """Test decoding array with custom indentation."""
    toon = """users[2]{id,name}:
    1,Alice
    2,Bob"""

    result = decode(toon)

    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }

    assert result == expected


def test_decode_strict_mode_correct_count():
    """Test strict mode with correct array count."""
    toon = """users[2]{id,name}:
  1,Alice
  2,Bob"""

    result = decode(toon, {'strict': True})

    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }

    assert result == expected


def test_decode_strict_mode_too_few_items():
    """Test strict mode raises error when array has fewer items than declared."""
    toon = """users[3]{id,name}:
  1,Alice
  2,Bob"""

    try:
        decode(toon, {'strict': True})
        assert False, 'Should have raised ValueError'
    except ValueError as e:
        assert 'Array length mismatch' in str(e)
        assert 'expected 3, got 2' in str(e)


def test_decode_non_strict_mode_too_few_items():
    """Test non-strict mode allows fewer items than declared."""
    toon = """users[5]{id,name}:
  1,Alice
  2,Bob"""

    result = decode(toon, {'strict': False})

    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }

    assert result == expected


def test_decode_strict_mode_list_array():
    """Test strict mode with list array."""
    toon = """items[2]:
  - item1
  - item2"""

    result = decode(toon, {'strict': True})

    expected = {
        'items': ['item1', 'item2']
    }

    assert result == expected


def test_decode_strict_mode_list_array_mismatch():
    """Test strict mode raises error for list array length mismatch."""
    toon = """items[4]:
  - item1
  - item2"""

    try:
        decode(toon, {'strict': True})
        assert False, 'Should have raised ValueError'
    except ValueError as e:
        assert 'Array length mismatch' in str(e)
        assert 'expected 4, got 2' in str(e)
