# TOON（面向Token的对象表示法）

[English](README.md) | [中文](README.zh-CN.md)

一种紧凑、人类可读的序列化格式，专为向大型语言模型传递结构化数据而设计，显著减少Token使用量。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 概述

TOON在实现**CSV般的紧凑性**的同时增加了**明确的结构**，非常适合：
- 降低LLM API调用的Token成本
- 提高上下文窗口效率
- 保持人类可读性
- 保留数据结构和类型

### 主要特性

- ✅ **紧凑**：比JSON结构化数据小30-60%
- ✅ **可读**：简洁、基于缩进的语法
- ✅ **结构化**：保留嵌套对象和数组
- ✅ **类型安全**：支持字符串、数字、布尔值、null
- ✅ **灵活**：多种分隔符选项（逗号、制表符、竖线）
- ✅ **智能**：对统一数组自动使用表格格式
- ✅ **高效**：对深层嵌套对象的键折叠

## 安装

```bash
pip install toonify
```

开发环境安装：
```bash
pip install toonify[dev]
```

支持Pydantic：
```bash
pip install toonify[pydantic]
```

## 快速开始

### Python API

```python
from toon import encode, decode

# 将Python字典编码为TOON
data = {
    'products': [
        {'sku': 'LAP-001', 'name': 'Gaming Laptop', 'price': 1299.99},
        {'sku': 'MOU-042', 'name': 'Wireless Mouse', 'price': 29.99}
    ]
}

toon_string = encode(data)
print(toon_string)
# 输出：
# products[2]{sku,name,price}:
#   LAP-001,Gaming Laptop,1299.99
#   MOU-042,Wireless Mouse,29.99

# 将TOON解码回Python
result = decode(toon_string)
assert result == data
```

### 命令行

```bash
# 将JSON编码为TOON
toon input.json -o output.toon

# 将TOON解码为JSON
toon input.toon -o output.json

# 使用管道
cat data.json | toon -e > data.toon

# 显示Token统计信息
toon data.json --stats
```

### Pydantic集成

TOON支持直接从Pydantic模型转换：

```python
from pydantic import BaseModel
from toon import encode_pydantic, decode_to_pydantic

# 定义Pydantic模型
class User(BaseModel):
    id: int
    name: str
    email: str

# 将Pydantic模型编码为TOON
users = [
    User(id=1, name='Alice', email='alice@example.com'),
    User(id=2, name='Bob', email='bob@example.com')
]

toon = encode_pydantic(users)
print(toon)
# 输出：
# [2]{id,name,email}:
#   1,Alice,alice@example.com
#   2,Bob,bob@example.com

# 将TOON解码回Pydantic模型
decoded_users = decode_to_pydantic(toon, User)
assert all(isinstance(u, User) for u in decoded_users)
```

**特性：**
- ✅ 直接从Pydantic模型转换（支持v1和v2）
- ✅ 支持嵌套模型
- ✅ 排除未设置、None或默认值
- ✅ 支持字段别名
- ✅ 解码时完全验证
- ✅ 往返转换

详见[examples/pydantic_usage.py](examples/pydantic_usage.py)。

## TOON格式规范

### 基本语法

```toon
# 简单的键值对
title: Machine Learning Basics
chapters: 12
published: true
```

### 数组

**原始数组**（内联）：
```toon
temperatures: [72.5,68.3,75.1,70.8,73.2]
categories: [electronics,computers,accessories]
```

**表格数组**（具有标题的统一对象）：
```toon
inventory[3]{sku,product,stock}:
  KB-789,Mechanical Keyboard,45
  MS-456,RGB Mouse Pad,128
  HD-234,USB Headset,67
```

**列表数组**（非统一或嵌套）：
```toon
tasks[2]:
  Complete documentation
  Review pull requests
```

### 嵌套对象

```toon
server:
  hostname: api-prod-01
  config:
    port: 8080
    region: us-east
```

### 引号规则

字符串仅在必要时使用引号：
- 包含特殊字符（`,`、`:`、`"`、换行符）
- 有前导/尾随空格
- 看起来像字面量（`true`、`false`、`null`）
- 为空字符串

```toon
simple: ProductName
quoted: "Product, Description"
escaped: "Size: 15\" display"
multiline: "First feature\nSecond feature"
```

## API参考

### `encode(data, options=None)`

将Python对象转换为TOON字符串。

**参数：**
- `data`：Python字典或列表
- `options`：可选字典，包含：
  - `delimiter`：`'comma'`（默认）、`'tab'`或`'pipe'`
  - `indent`：每级缩进的空格数（默认：2）
  - `key_folding`：`'off'`（默认）或`'safe'`
  - `flatten_depth`：键折叠的最大深度（默认：None）

**示例：**
```python
toon = encode(data, {
    'delimiter': 'tab',
    'indent': 4,
    'key_folding': 'safe'
})
```

### `decode(toon_string, options=None)`

将TOON字符串转换为Python对象。

**参数：**
- `toon_string`：TOON格式字符串
- `options`：可选字典，包含：
  - `strict`：严格验证结构（默认：True）
  - `expand_paths`：`'off'`（默认）或`'safe'`
  - `default_delimiter`：默认分隔符（默认：`','`）

**示例：**
```python
data = decode(toon_string, {
    'expand_paths': 'safe',
    'strict': False
})
```

### `encode_pydantic(model, options=None, exclude_unset=False, exclude_none=False, exclude_defaults=False, by_alias=False)`

将Pydantic模型转换为TOON字符串。

**参数：**
- `model`：Pydantic模型实例或模型实例列表
- `options`：与`encode()`函数相同
- `exclude_unset`：如果为True，排除未明确设置的字段
- `exclude_none`：如果为True，排除None值字段
- `exclude_defaults`：如果为True，排除具有默认值的字段
- `by_alias`：如果为True，使用字段别名而不是字段名称

**示例：**
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

将TOON字符串解码为Pydantic模型。

**参数：**
- `toon_string`：TOON格式字符串
- `model_class`：要实例化的Pydantic模型类
- `options`：与`decode()`函数相同

**返回：**
- Pydantic模型实例或实例列表（取决于输入）

**示例：**
```python
from pydantic import BaseModel
from toon import decode_to_pydantic

class User(BaseModel):
    id: int
    name: str

toon = "id: 1\nname: Alice"
user = decode_to_pydantic(toon, User)
```

## CLI使用

```
用法：toon [-h] [-o OUTPUT] [-e] [-d] [--delimiter {comma,tab,pipe}]
            [--indent INDENT] [--stats] [--no-strict]
            [--key-folding {off,safe}] [--flatten-depth DEPTH]
            [--expand-paths {off,safe}]
            [input]

TOON (Token-Oriented Object Notation) - 在JSON和TOON格式之间转换

位置参数：
  input                 输入文件路径（或"-"表示stdin）

可选参数：
  -h, --help            显示帮助信息并退出
  -o, --output OUTPUT   输出文件路径（默认：stdout）
  -e, --encode          强制编码模式（JSON到TOON）
  -d, --decode          强制解码模式（TOON到JSON）
  --delimiter {comma,tab,pipe}
                        数组分隔符（默认：comma）
  --indent INDENT       缩进大小（默认：2）
  --stats               显示Token统计信息
  --no-strict           禁用严格验证（仅解码）
  --key-folding {off,safe}
                        键折叠模式（仅编码）
  --flatten-depth DEPTH 最大键折叠深度（仅编码）
  --expand-paths {off,safe}
                        路径扩展模式（仅解码）
```

## 高级特性

### 键折叠

将单键链折叠为点分隔路径：

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

# 使用key_folding='safe'
toon = encode(data, {'key_folding': 'safe'})
# 输出：api.response.product.title: Wireless Keyboard
```

### 路径扩展

将点分隔的键扩展为嵌套对象：

```python
toon = 'store.location.zipcode: 10001'

# 使用expand_paths='safe'
data = decode(toon, {'expand_paths': 'safe'})
# 结果：{'store': {'location': {'zipcode': 10001}}}
```

### 自定义分隔符

选择最适合您数据的分隔符：

```python
# 制表符分隔符（更适合类似电子表格的数据）
toon = encode(data, {'delimiter': 'tab'})

# 竖线分隔符（当数据包含逗号时）
toon = encode(data, {'delimiter': 'pipe'})
```

## 格式比较

### JSON vs TOON

**JSON**（247字节）：
```json
{
  "products": [
    {"id": 101, "name": "Laptop Pro", "price": 1299},
    {"id": 102, "name": "Magic Mouse", "price": 79},
    {"id": 103, "name": "USB-C Cable", "price": 19}
  ]
}
```

**TOON**（98字节，**减少60%**）：
```toon
products[3]{id,name,price}:
  101,Laptop Pro,1299
  102,Magic Mouse,79
  103,USB-C Cable,19
```

### 何时使用TOON

**使用TOON的场景：**
- ✅ 向LLM API传递数据（降低Token成本）
- ✅ 处理统一的表格数据
- ✅ 上下文窗口受限
- ✅ 重视人类可读性

**使用JSON的场景：**
- ❌ 需要最大兼容性
- ❌ 数据高度不规则/嵌套
- ❌ 使用仅支持JSON的现有工具

## 开发

### 设置

```bash
git clone https://github.com/ScrapeGraphAI/toonify.git
cd toonify
pip install -e .[dev]
```

### 运行测试

```bash
pytest
pytest --cov=toon --cov-report=term-missing
```

### 运行示例

```bash
python examples/basic_usage.py
python examples/advanced_features.py
```

## 性能

TOON通常实现：
- 与JSON相比，结构化数据**减少30-60%的大小**
- 表格数据**减少40-70%的Token**
- **最小的开销**用于编码/解码（典型有效负载<1ms）

## 贡献

欢迎贡献！请：

1. Fork仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 进行更改并编写测试
4. 运行测试（`pytest`）
5. 提交更改（`git commit -m 'Add amazing feature'`）
6. 推送到分支（`git push origin feature/amazing-feature`）
7. 打开Pull Request

## 许可证

MIT许可证 - 详情请参见[LICENSE](LICENSE)文件。

## 致谢

Python实现受[toon-format/toon](https://github.com/toon-format/toon)的TypeScript TOON库启发。

## 链接

- **GitHub**：https://github.com/ScrapeGraphAI/toonify
- **PyPI**：https://pypi.org/project/toonify/
- **文档**：https://github.com/ScrapeGraphAI/toonify#readme
- **格式规范**：https://github.com/toon-format/toon

---

由[ScrapeGraph团队](https://scrapegraphai.com)用心制作

<p align="center">
  <img src="https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/docs/assets/scrapegraphai_logo.png" alt="ScrapeGraphAI Logo" width="250">
</p>

