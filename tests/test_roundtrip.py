"""Tests for round-trip encoding and decoding."""
import pytest
from toon import encode, decode


def test_roundtrip_simple_object():
    """Test round-trip of simple object."""
    original = {
        'name': 'Alice',
        'age': 30,
        'active': True
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_nested_object():
    """Test round-trip of nested object."""
    original = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_primitive_array():
    """Test round-trip of primitive arrays."""
    original = {
        'numbers': [1, 2, 3, 4, 5],
        'names': ['Alice', 'Bob', 'Charlie'],
        'mixed': [1, 'text', True, None]
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_tabular_array():
    """Test round-trip of tabular array."""
    original = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'},
            {'id': 3, 'name': 'Charlie', 'role': 'guest'}
        ]
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_empty_structures():
    """Test round-trip of empty structures."""
    original = {
        'empty_object': {},
        'empty_array': [],
        'nested': {
            'also_empty': {}
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_special_strings():
    """Test round-trip of strings requiring quotes."""
    original = {
        'comma': 'hello, world',
        'colon': 'key: value',
        'quote': 'He said "hello"',
        'newline': 'line1\nline2',
        'spaces': '  padded  ',
        'looks_like_bool': 'true',
        'looks_like_null': 'null'
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_complex_structure():
    """Test round-trip of complex structure."""
    original = {
        'project': 'TOON',
        'version': '1.0.0',
        'description': 'A token-efficient format',
        'features': ['compact', 'readable', 'structured'],
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ],
        'metadata': {
            'created': '2024-01-01',
            'author': 'TOON Contributors',
            'stats': {
                'files': 10,
                'lines': 1000
            }
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_with_delimiters():
    """Test round-trip with different delimiters."""
    original = {
        'values': [1, 2, 3],
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    # Tab delimiter
    toon_tab = encode(original, {'delimiter': 'tab'})
    result_tab = decode(toon_tab)
    assert result_tab == original
    
    # Pipe delimiter
    toon_pipe = encode(original, {'delimiter': 'pipe'})
    result_pipe = decode(toon_pipe)
    assert result_pipe == original


def test_roundtrip_key_folding_and_expansion():
    """Test round-trip with key folding and path expansion."""
    original = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    
    # Encode with key folding
    toon = encode(original, {'key_folding': 'safe'})
    
    # Decode with path expansion
    result = decode(toon, {'expand_paths': 'safe'})
    
    assert result == original


def test_roundtrip_multiple_iterations():
    """Test multiple encode-decode cycles maintain consistency."""
    original = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'count': 2
    }
    
    # First cycle
    toon1 = encode(original)
    result1 = decode(toon1)
    
    # Second cycle
    toon2 = encode(result1)
    result2 = decode(toon2)
    
    # Third cycle
    toon3 = encode(result2)
    result3 = decode(toon3)
    
    # All should be equal
    assert result1 == original
    assert result2 == original
    assert result3 == original
    assert toon1 == toon2 == toon3


def test_roundtrip_delimiter_indicators():
    """Test round-trip with delimiter indicators in headers."""
    original = {
        'tab_data': [
            {'id': 1, 'value': 'A'},
            {'id': 2, 'value': 'B'}
        ],
        'pipe_data': [
            {'code': 'X', 'qty': 10},
            {'code': 'Y', 'qty': 20}
        ]
    }

    # Test with tab delimiter
    toon_tab = encode(original, {'delimiter': 'tab'})
    assert '[2\t]{id,value}:' in toon_tab
    result_tab = decode(toon_tab)
    assert result_tab == original

    # Test with pipe delimiter
    toon_pipe = encode(original, {'delimiter': 'pipe'})
    assert '[2|]{id,value}:' in toon_pipe or '[2|]{code,qty}:' in toon_pipe
    result_pipe = decode(toon_pipe)
    assert result_pipe == original

    # Test with comma delimiter (no indicator)
    toon_comma = encode(original, {'delimiter': 'comma'})
    assert '[2]{id,value}:' in toon_comma
    assert '\t' not in toon_comma  # No tab indicator
    assert '[2|]' not in toon_comma  # No pipe indicator
    result_comma = decode(toon_comma)
    assert result_comma == original


def test_roundtrip_list_array_with_dashes():
    """Test round-trip with list array dash markers."""
    original = {
        'mixed': [
            'text',
            42,
            {'nested': 'object'},
            True
        ],
        'list_with_objects': [
            {'id': 1},
            {'id': 2, 'name': 'extra field'}  # Non-uniform, so list format
        ]
    }

    # Encode
    toon = encode(original)

    # Verify dash markers are present in mixed array
    assert '- text' in toon
    assert '- 42' in toon
    assert '- nested: object' in toon
    assert '- true' in toon

    # Decode
    result = decode(toon)

    # Should match original
    assert result == original

    # Second round-trip
    toon2 = encode(result)
    result2 = decode(toon2)
    assert result2 == original


def test_roundtrip_datetime_objects():
    """Test round-trip with datetime objects (encodes to ISO strings)."""
    from datetime import datetime, date

    original = {
        'created': datetime(2024, 1, 1, 12, 30, 45),
        'birth_date': date(1990, 5, 20),
        'events': [
            {'name': 'Start', 'time': datetime(2024, 1, 1, 0, 0, 0)},
            {'name': 'End', 'time': datetime(2024, 12, 31, 23, 59, 59)}
        ]
    }

    # Encode
    toon = encode(original)

    # Verify ISO format strings are present
    assert '2024-01-01T12:30:45' in toon
    assert '1990-05-20' in toon

    # Decode (datetimes become strings)
    result = decode(toon)

    # After decode, datetimes are strings
    expected_decoded = {
        'created': '2024-01-01T12:30:45',
        'birth_date': '1990-05-20',
        'events': [
            {'name': 'Start', 'time': '2024-01-01T00:00:00'},
            {'name': 'End', 'time': '2024-12-31T23:59:59'}
        ]
    }

    assert result == expected_decoded

    # Second encode should produce same TOON string
    toon2 = encode(result)
    assert toon == toon2

    # Third decode should match second
    result2 = decode(toon2)
    assert result2 == expected_decoded


def test_roundtrip_scientific_notation_suppression():
    """Test round-trip with scientific notation suppression."""
    original = {
        'small': 0.000001,
        'smaller': 0.0000001,
        'large': 15000000000000000.0,
        'very_large': 1.23e20,
        'normal': 3.14159,
        'values': [0.000001, 1.5e16]
    }

    # First encode
    toon = encode(original)

    # Should not have scientific notation for reasonable values
    assert '0.000001' in toon
    assert '0.0000001' in toon
    assert '15000000000000000' in toon
    assert '123000000000000000000' in toon

    # Decode
    result = decode(toon)

    # Values should match (allowing for float precision)
    assert result['small'] == 0.000001
    assert result['smaller'] == 0.0000001
    assert result['large'] == 15000000000000000.0
    assert result['very_large'] == 1.23e20
    assert result['normal'] == 3.14159

    # Second encode should produce same TOON
    toon2 = encode(result)
    assert toon == toon2

    # Third decode should match
    result2 = decode(toon2)
    assert result2 == result


def test_roundtrip_extreme_scientific_notation():
    """Test round-trip with extreme values that keep scientific notation."""
    original = {
        'very_small': 1.23e-150,
        'very_large': 1.23e150
    }

    # First encode
    toon = encode(original)

    # Extreme values should keep scientific notation
    assert 'e' in toon.lower() or 'E' in toon

    # Decode
    result = decode(toon)

    # Values should match
    assert result['very_small'] == 1.23e-150
    assert result['very_large'] == 1.23e150

    # Second encode should produce same TOON
    toon2 = encode(result)
    assert toon == toon2


def test_roundtrip_root_inline_array():
    """Test round-trip with root-level inline array."""
    original = [1, 2, 3, 4, 5]

    # First encode
    toon = encode(original)
    assert toon == '[1,2,3,4,5]'

    # Decode
    result = decode(toon)
    assert result == original

    # Second encode
    toon2 = encode(result)
    assert toon2 == toon


def test_roundtrip_root_tabular_array():
    """Test round-trip with root-level tabular array."""
    original = [
        {'id': 1, 'name': 'Alice', 'active': True},
        {'id': 2, 'name': 'Bob', 'active': False},
        {'id': 3, 'name': 'Charlie', 'active': True}
    ]

    # First encode
    toon = encode(original)
    assert '[3]{id,name,active}:' in toon

    # Decode
    result = decode(toon)
    assert result == original

    # Second encode
    toon2 = encode(result)
    assert toon2 == toon


def test_roundtrip_root_list_array():
    """Test round-trip with root-level list array."""
    original = [
        1,
        'text',
        True,
        {'nested': 'object'},
        [1, 2, 3]
    ]

    # First encode
    toon = encode(original)
    assert '[5]:' in toon
    assert '- 1' in toon
    assert '- nested: object' in toon

    # Decode
    result = decode(toon)
    assert result == original

    # Second encode
    toon2 = encode(result)
    assert toon2 == toon
