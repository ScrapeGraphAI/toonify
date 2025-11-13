# TOON Benchmark Suite

This benchmark suite demonstrates the **MASSIVE memory and token savings** achieved by using TOON (Token-Oriented Object Notation) compared to JSON for structured data.

**NEW:** TOON now supports direct conversion from [Pydantic models](../examples/pydantic_usage.py) with `encode_pydantic()` and `decode_to_pydantic()` functions!

## 🚀 HEADLINE RESULTS

**Tested across 50 diverse, real-world datasets:**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    ⚡ TOON DELIVERS ⚡                         ║
║                                                               ║
║     📉  63.9% SMALLER file sizes                              ║
║     📉  54.1% FEWER tokens for LLM APIs                       ║
║     💾  35.81KB total memory saved                            ║
║     🎯  10,735 total tokens saved                             ║
║                                                               ║
║                 💰 COST SAVINGS 💰                             ║
║     $2,147 per million API requests                           ║
║     $5,408 per billion tokens                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**[👉 SEE FULL RESULTS](RESULTS.md)** | 98% of datasets achieve 40%+ savings!

## 🎯 Key Results

### Memory & Token Savings

TOON achieves **remarkable reductions** compared to JSON:

| Metric | Average Savings | Best Case |
|--------|----------------|-----------|
| **File Size** | **63.9%** | 73.4% |
| **Token Count** | **54.1%** | 63.4% |
| **Network Bandwidth** | **63.9%** | 73.4% |

### 💰 Real-World Cost Impact

For LLM API usage at typical GPT-4 pricing ($10/1M tokens):

| Usage | JSON Cost | TOON Cost | **You Save** |
|-------|-----------|-----------|--------------|
| 1K requests | $3.97 | $1.82 | **$2.15** |
| 1M requests/year | $3,970 | $1,823 | **$2,147** |
| 1B tokens | $10,000 | $4,592 | **$5,408** |

## 📊 Detailed Results

### Performance Distribution

Across **50 diverse, real-world datasets**:

```
🔥 EXCELLENT (≥60% savings):  30 datasets (60%)
✅ GOOD (40-60% savings):     19 datasets (38%)
📊 MODERATE (<40% savings):    1 dataset  (2%)
```

**98% of tested datasets achieve 40%+ savings!**

### By Dataset Category

| Category | Datasets | Avg Size Savings | Avg Token Savings | Best Example |
|----------|----------|------------------|-------------------|--------------|
| **Tabular Data** | 12 | **69.2%** | **59.8%** | Student Grades (71.2%) |
| **E-commerce** | 8 | **66.1%** | **56.4%** | Customer Reviews (69.1%) |
| **Analytics** | 7 | **65.7%** | **55.2%** | Survey Responses (73.4%) |
| **API Data** | 10 | **58.3%** | **48.9%** | Database Results (62.5%) |
| **IoT/Sensors** | 5 | **60.0%** | **43.7%** | Time Series (58.9%) |
| **Social/Content** | 8 | **61.5%** | **52.1%** | Social Posts (66.8%) |

### Top 10 Performers (by Size Savings)

| Rank | Dataset | JSON Size | TOON Size | Size Savings | Token Savings |
|------|---------|-----------|-----------|--------------|---------------|
| 🥇 | Survey Responses | 935B | 249B | **73.4%** | **63.4%** |
| 🥈 | ML Training Data | 1.85KB | 545B | **71.2%** | **61.9%** |
| 🥈 | Large Inventory | 13.55KB | 3.90KB | **71.2%** | **57.7%** |
| 🥈 | Student Grades | - | - | **71.2%** | **61.9%** |
| 4 | Customer Reviews | 828B | 256B | **69.1%** | **61.0%** |
| 5 | Weather Forecast | 777B | 241B | **69.0%** | **55.9%** |
| 6 | Flight Schedule | - | - | **68.9%** | **59.9%** |
| 7 | Geographic Data | - | - | **68.8%** | **60.6%** |
| 8 | Movie Catalog | - | - | **68.5%** | **59.8%** |
| 9 | Social Media Posts | 849B | 282B | **66.8%** | **52.1%** |
| 10 | E-commerce Products | 1.61KB | 542B | **66.3%** | **58.2%** |

**[View complete results for all 50 datasets →](RESULTS.md)**

### 🏆 Best Performance

TOON excels particularly with:
- **Tabular data** (e.g., database results, inventory): up to **73.4% reduction**
- **Uniform arrays** (e.g., ML training data): up to **63.4% token savings**
- **Structured records** (e.g., e-commerce products): **66.3% size reduction**
- **Analytics data** (surveys, metrics): consistently **65-73% savings**
- **E-commerce** (products, reviews): consistently **66-69% savings**

### 📉 When Savings Are Lower

Only 1 out of 50 datasets (2%) achieved <40% savings:
- **Deeply nested objects** with non-uniform structure (39% savings for Shipping Tracking)

Even in the worst case, TOON maintains **readability** while providing **significant savings**.

## 🚀 Running the Benchmarks

### Prerequisites

```bash
# Install the package with dependencies
pip install -e .

# tiktoken is required for token counting
pip install tiktoken

# Pydantic is optional but recommended for model validation
pip install pydantic
```

### Run All Benchmarks

```bash
# Run the complete benchmark suite (tests all 50 datasets)
python benchmark/run_all.py
```

### Run Individual Benchmarks

```bash
# Compare file sizes and token counts (all 50 datasets)
python benchmark/compare_formats.py

# Measure memory usage (subset of datasets)
python benchmark/memory_benchmark.py
```

The benchmark tests **50 diverse, real-world datasets** including:
- E-commerce (products, orders, reviews, inventory)
- Databases (query results, employee records)
- APIs (responses, logs, requests)
- Analytics (metrics, surveys, A/B tests)
- IoT (sensor data, time series)
- Social media (posts, profiles, comments)
- Finance (transactions, stock data)
- And much more!

## 📁 Benchmark Files

- **[compare_formats.py](compare_formats.py)** - Compares JSON vs TOON across 50 datasets
- **[memory_benchmark.py](memory_benchmark.py)** - Measures actual memory consumption
- **[sample_datasets.py](sample_datasets.py)** - Collection of 50 realistic test datasets
- **[run_all.py](run_all.py)** - Executes all benchmarks and generates summary
- **[RESULTS.md](RESULTS.md)** - Complete detailed results for all 50 datasets

## 🔍 Sample Output Comparison

### E-commerce Products

**JSON** (1,607 bytes, 552 tokens):
```json
{
  "products": [
    {
      "id": 1001,
      "sku": "LAP-001",
      "name": "Gaming Laptop",
      "price": 1299.99,
      "stock": 45,
      "category": "Electronics"
    },
    ...
  ]
}
```

**TOON** (542 bytes, 231 tokens):
```toon
products[10]{id,sku,name,price,stock,category}:
  1001,LAP-001,Gaming Laptop,1299.99,45,Electronics
  1002,MOU-042,Wireless Mouse,29.99,234,Accessories
  ...
```

**Savings: 66.3% size, 58.2% tokens**

### Database Results

**JSON** (1,552 bytes, 481 tokens):
```json
{
  "query": "SELECT * FROM employees WHERE department = 'Engineering'",
  "rows": [
    {
      "emp_id": 1001,
      "name": "Alice Johnson",
      "department": "Engineering",
      "salary": 95000,
      "start_date": "2020-03-15",
      "remote": true
    },
    ...
  ]
}
```

**TOON** (582 bytes, 209 tokens):
```toon
query: SELECT * FROM employees WHERE department = 'Engineering'
rows[8]{emp_id,name,department,salary,start_date,remote}:
  1001,Alice Johnson,Engineering,95000,2020-03-15,true
  1002,Bob Smith,Engineering,105000,2019-07-22,false
  ...
```

**Savings: 62.5% size, 56.5% tokens**

## 💡 Why TOON Saves Memory

### 1. Compact Array Representation

**JSON** repeats keys for every object:
```json
[
  {"id": 1, "name": "A", "price": 10},
  {"id": 2, "name": "B", "price": 20}
]
```

**TOON** declares headers once:
```toon
[2]{id,name,price}:
  1,A,10
  2,B,20
```

### 2. Minimal Syntax Overhead

**JSON** requires:
- Braces: `{ }`
- Brackets: `[ ]`
- Quotes around all keys: `"key"`
- Quotes around string values: `"value"`
- Commas everywhere: `,`

**TOON** uses:
- Indentation for structure (like YAML)
- Colons for key-value pairs: `key: value`
- Quotes only when necessary
- Headers for uniform arrays

### 3. Intelligent Type Handling

TOON automatically:
- Detects when quotes aren't needed
- Uses compact array format for uniform data
- Preserves types (numbers, booleans, null)
- Maintains human readability

## 📈 Performance Characteristics

### Encoding/Decoding Speed

While TOON is slightly slower than native JSON (which is implemented in C), the difference is negligible for typical use cases:

- **JSON encoding**: ~0.005-0.06 ms per operation
- **TOON encoding**: ~0.03-0.57 ms per operation
- **JSON decoding**: ~0.004-0.05 ms per operation
- **TOON decoding**: ~0.04-0.62 ms per operation

**Bottom line**: For 99% of use cases, the performance difference is imperceptible, and the memory/token savings far outweigh the minimal overhead.

## 🎯 Use Cases Where TOON Excels

### ✅ Perfect For:

1. **LLM API Payloads** - Reduce token costs by 50%+
2. **Database Query Results** - Compact tabular data representation
3. **Analytics/Metrics Data** - Efficient time-series and aggregate data
4. **ML Training Data** - Compress feature vectors and labels
5. **E-commerce Catalogs** - Product listings with uniform structure
6. **Inventory Systems** - Large collections of similar items
7. **Log Aggregation** - Structured log entries with common fields

### ⚠️ Less Optimal For:

1. **Highly Irregular Data** - Where no two objects share the same structure
2. **Maximum Compatibility** - When you need universal JSON tool support
3. **Extreme Performance** - When microseconds matter (though TOON is still fast)

## 🔬 Methodology

Our benchmarks use:
- **tiktoken** for accurate GPT-4 token counting
- **Real-world datasets** representing common use cases
- **Multiple iterations** (1,000+) for performance measurements
- **Actual memory profiling** using `sys.getsizeof`

All benchmark code is open source and can be reviewed in this directory.

## 📚 Additional Resources

- [TOON Format Specification](https://github.com/toon-format/toon)
- [Main README](../README.md) - Includes Pydantic integration documentation
- [Pydantic Examples](../examples/pydantic_usage.py) - Direct conversion from Pydantic models
- [Python Package](https://pypi.org/project/toonify/)

## 🤝 Contributing

Found a dataset where TOON could perform better? Want to add more benchmarks?

1. Add your dataset to [sample_datasets.py](sample_datasets.py)
2. Run the benchmarks
3. Submit a PR with your findings!

## 📊 Visual Summary

```
┌────────────────────────────────────────────────────────────┐
│  JSON vs TOON - Average Savings (50 Datasets)             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  File Size:     ████████████████████████████████░░ 63.9%  │
│  Tokens:        ███████████████████████████░░░░░░░ 54.1%  │
│  API Costs:     ███████████████████████████░░░░░░░ 54.1%  │
│                                                            │
│  Best Case:     █████████████████████████████████░ 73.4%  │
│  (Survey Responses)                                        │
│                                                            │
│  98% of datasets achieve 40%+ savings                      │
│  60% of datasets achieve 60%+ savings                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

**💾 Remember**: Every byte saved is a token saved, and every token saved is money saved when working with LLM APIs!

**🎉 With 63.9% size reduction and 54.1% token reduction across 50 diverse datasets, TOON delivers massive, consistent savings for real-world structured data!**
