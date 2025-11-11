<p align="center">
  <img src="assets/toonify.png" alt="Toonify Logo" width="400">
</p>

# TOON (Token-Oriented Object Notation)

[English](README.md) | [中文](assets/README.zh-CN.md)

A compact, human-readable serialization format designed for passing structured data to Large Language Models with significantly reduced token usage.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

TOON achieves **CSV-like compactness** while adding **explicit structure**, making it ideal for:
- Reducing token costs in LLM API calls
- Improving context window efficiency
- Maintaining human readability
- Preserving data structure and types

### Key Features

- ✅ **Compact**: 30-60% smaller than JSON for structured data
- ✅ **Readable**: Clean, indentation-based syntax
- ✅ **Structured**: Preserves nested objects and arrays
- ✅ **Type-safe**: Supports strings, numbers, booleans, null
- ✅ **Flexible**: Multiple delimiter options (comma, tab, pipe)
- ✅ **Smart**: Automatic tabular format for uniform arrays
- ✅ **Efficient**: Key folding for deeply nested objects

## Installation

```bash
pip install toonify
```

For development:
```bash
pip install toonify[dev]
```

With Pydantic support:
```bash
pip install toonify[pydantic]
```

## Quick Start

### Python API

```python
from toon import encode, decode

# Encode Python dict to TOON
data = {
    'products': [
        {'sku': 'LAP-001', 'name': 'Gaming Laptop', 'price': 1299.99},
        {'sku': 'MOU-042', 'name': 'Wireless Mouse', 'price': 29.99}
    ]
}

toon_string = encode(data)
print(toon_string)
# Output:
# products[2]{sku,name,price}:
#   LAP-001,Gaming Laptop,1299.99
#   MOU-042,Wireless Mouse,29.99

# Decode TOON back to Python
result = decode(toon_string)
assert result == data
```

### Command Line

```bash
# Encode JSON to TOON
toon input.json -o output.toon

# Decode TOON to JSON
toon input.toon -o output.json

# Use with pipes
cat data.json | toon -e > data.toon

# Show token statistics
toon data.json --stats
```

### Pydantic Integration

TOON supports direct conversion from Pydantic models:

```python
from pydantic import BaseModel
from toon import encode_pydantic, decode_to_pydantic

# Define Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str

# Encode Pydantic models to TOON
users = [
    User(id=1, name='Alice', email='alice@example.com'),
    User(id=2, name='Bob', email='bob@example.com')
]

toon = encode_pydantic(users)
print(toon)
# Output:
# [2]{id,name,email}:
#   1,Alice,alice@example.com
#   2,Bob,bob@example.com

# Decode TOON back to Pydantic models
decoded_users = decode_to_pydantic(toon, User)
assert all(isinstance(u, User) for u in decoded_users)
```

**Features:**
- ✅ Direct conversion from Pydantic models (v1 and v2)
- ✅ Support for nested models
- ✅ Exclude unset, None, or default values
- ✅ Field aliases support
- ✅ Full validation on decode
- ✅ Round-trip conversion

See [examples/pydantic_usage.py](examples/pydantic_usage.py) for more examples.

## TOON Format Specification

### Basic Syntax

```toon
# Simple key-value pairs
title: Machine Learning Basics
chapters: 12
published: true
```

### Arrays

**Primitive arrays** (inline):
```toon
temperatures: [72.5,68.3,75.1,70.8,73.2]
categories: [electronics,computers,accessories]
```

**Tabular arrays** (uniform objects with header):
```toon
inventory[3]{sku,product,stock}:
  KB-789,Mechanical Keyboard,45
  MS-456,RGB Mouse Pad,128
  HD-234,USB Headset,67
```

**List arrays** (non-uniform or nested):
```toon
tasks[2]:
  Complete documentation
  Review pull requests
```

### Nested Objects

```toon
server:
  hostname: api-prod-01
  config:
    port: 8080
    region: us-east
```

### Quoting Rules

Strings are quoted only when necessary:
- Contains special characters (`,`, `:`, `"`, newlines)
- Has leading/trailing whitespace
- Looks like a literal (`true`, `false`, `null`)
- Is empty

```toon
simple: ProductName
quoted: "Product, Description"
escaped: "Size: 15\" display"
multiline: "First feature\nSecond feature"
```

## API Reference

### `encode(data, options=None)`

Convert Python object to TOON string.

**Parameters:**
- `data`: Python dict or list
- `options`: Optional dict with:
  - `delimiter`: `'comma'` (default), `'tab'`, or `'pipe'`
  - `indent`: Number of spaces per level (default: 2)
  - `key_folding`: `'off'` (default) or `'safe'`
  - `flatten_depth`: Max depth for key folding (default: None)

**Example:**
```python
toon = encode(data, {
    'delimiter': 'tab',
    'indent': 4,
    'key_folding': 'safe'
})
```

### `decode(toon_string, options=None)`

Convert TOON string to Python object.

**Parameters:**
- `toon_string`: TOON formatted string
- `options`: Optional dict with:
  - `strict`: Validate structure strictly (default: True)
  - `expand_paths`: `'off'` (default) or `'safe'`
  - `default_delimiter`: Default delimiter (default: `','`)

**Example:**
```python
data = decode(toon_string, {
    'expand_paths': 'safe',
    'strict': False
})
```

### `encode_pydantic(model, options=None, exclude_unset=False, exclude_none=False, exclude_defaults=False, by_alias=False)`

Convert Pydantic model(s) to TOON string.

**Parameters:**
- `model`: Pydantic model instance or list of model instances
- `options`: Same as `encode()` function
- `exclude_unset`: If True, exclude fields that were not explicitly set
- `exclude_none`: If True, exclude fields with None values
- `exclude_defaults`: If True, exclude fields with default values
- `by_alias`: If True, use field aliases instead of field names

**Example:**
```python
from pydantic import BaseModel
from toon import encode_pydantic

class User(BaseModel):
    id: int
    name: str
    email: str | None = None

user = User(id=1, name='Alice')
toon = encode_pydantic(user, exclude_none=True)
```

### `decode_to_pydantic(toon_string, model_class, options=None)`

Decode TOON string to Pydantic model(s).

**Parameters:**
- `toon_string`: TOON formatted string
- `model_class`: Pydantic model class to instantiate
- `options`: Same as `decode()` function

**Returns:**
- Pydantic model instance or list of instances (depending on input)

**Example:**
```python
from pydantic import BaseModel
from toon import decode_to_pydantic

class User(BaseModel):
    id: int
    name: str

toon = "id: 1\nname: Alice"
user = decode_to_pydantic(toon, User)
```

## CLI Usage

```
usage: toon [-h] [-o OUTPUT] [-e] [-d] [--delimiter {comma,tab,pipe}]
            [--indent INDENT] [--stats] [--no-strict]
            [--key-folding {off,safe}] [--flatten-depth DEPTH]
            [--expand-paths {off,safe}]
            [input]

TOON (Token-Oriented Object Notation) - Convert between JSON and TOON formats

positional arguments:
  input                 Input file path (or "-" for stdin)

optional arguments:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output file path (default: stdout)
  -e, --encode          Force encode mode (JSON to TOON)
  -d, --decode          Force decode mode (TOON to JSON)
  --delimiter {comma,tab,pipe}
                        Array delimiter (default: comma)
  --indent INDENT       Indentation size (default: 2)
  --stats               Show token statistics
  --no-strict           Disable strict validation (decode only)
  --key-folding {off,safe}
                        Key folding mode (encode only)
  --flatten-depth DEPTH Maximum key folding depth (encode only)
  --expand-paths {off,safe}
                        Path expansion mode (decode only)
```

## Advanced Features

### Key Folding

Collapse single-key chains into dotted paths:

```python
data = {
    'api': {
        'response': {
            'product': {
                'title': 'Wireless Keyboard'
            }
        }
    }
}

# With key_folding='safe'
toon = encode(data, {'key_folding': 'safe'})
# Output: api.response.product.title: Wireless Keyboard
```

### Path Expansion

Expand dotted keys into nested objects:

```python
toon = 'store.location.zipcode: 10001'

# With expand_paths='safe'
data = decode(toon, {'expand_paths': 'safe'})
# Result: {'store': {'location': {'zipcode': 10001}}}
```

### Custom Delimiters

Choose the delimiter that best fits your data:

```python
# Tab delimiter (better for spreadsheet-like data)
toon = encode(data, {'delimiter': 'tab'})

# Pipe delimiter (when data contains commas)
toon = encode(data, {'delimiter': 'pipe'})
```

## Format Comparison

### JSON vs TOON

**JSON** (247 bytes):
```json
{
  "products": [
    {"id": 101, "name": "Laptop Pro", "price": 1299},
    {"id": 102, "name": "Magic Mouse", "price": 79},
    {"id": 103, "name": "USB-C Cable", "price": 19}
  ]
}
```

**TOON** (98 bytes, **60% reduction**):
```toon
products[3]{id,name,price}:
  101,Laptop Pro,1299
  102,Magic Mouse,79
  103,USB-C Cable,19
```

### When to Use TOON

**Use TOON when:**
- ✅ Passing data to LLM APIs (reduce token costs)
- ✅ Working with uniform tabular data
- ✅ Context window is limited
- ✅ Human readability matters

**Use JSON when:**
- ❌ Maximum compatibility is required
- ❌ Data is highly irregular/nested
- ❌ Working with existing JSON-only tools

## Development

### Setup

```bash
git clone https://github.com/ScrapeGraphAI/toonify.git
cd toonify
pip install -e .[dev]
```

### Running Tests

```bash
pytest
pytest --cov=toon --cov-report=term-missing
```

### Running Examples

```bash
python examples/basic_usage.py
python examples/advanced_features.py
```

## Performance

TOON typically achieves:
- **30-60% size reduction** vs JSON for structured data
- **40-70% token reduction** with tabular data
- **Minimal overhead** in encoding/decoding (<1ms for typical payloads)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Python implementation inspired by the TypeScript TOON library at [toon-format/toon](https://github.com/toon-format/toon).

## Links

- **GitHub**: https://github.com/ScrapeGraphAI/toonify
- **PyPI**: https://pypi.org/project/toonify/
- **Documentation**: https://github.com/ScrapeGraphAI/toonify#readme
- **Format Spec**: https://github.com/toon-format/toon

---

Made with love by the [ScrapeGraph team](https://scrapegraphai.com)

<p align="center">
  <img src="https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/docs/assets/scrapegraphai_logo.png" alt="ScrapeGraphAI Logo" width="250">
</p>
