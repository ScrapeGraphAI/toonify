"""Examples demonstrating Pydantic model conversion with TOON."""
try:
    from pydantic import BaseModel, Field
    from toon import encode_pydantic, decode_to_pydantic, encode
    import json
except ImportError as e:
    print(f"Error: {e}")
    print("Please install pydantic: pip install pydantic")
    exit(1)


# Define Pydantic models
class Address(BaseModel):
    """Address model."""
    street: str
    city: str
    state: str
    zipcode: str


class User(BaseModel):
    """User model with optional fields."""
    id: int
    name: str
    email: str
    age: int | None = None
    active: bool = True
    address: Address | None = None


class Product(BaseModel):
    """Product model."""
    sku: str
    name: str
    price: float
    stock: int
    tags: list[str] = []


class Order(BaseModel):
    """Order model with nested products."""
    order_id: str = Field(alias='orderId')
    customer_name: str = Field(alias='customerName')
    products: list[Product]
    total: float


def example_simple_model():
    """Example: Simple Pydantic model to TOON."""
    print("=== Simple Pydantic Model ===")
    
    user = User(
        id=1,
        name='Alice Smith',
        email='alice@example.com',
        age=30,
        active=True
    )
    
    print("Python object:")
    print(f"  {user}")
    print()
    
    toon = encode_pydantic(user)
    print("TOON format:")
    print(toon)
    print()


def example_list_of_models():
    """Example: List of uniform Pydantic models (tabular format)."""
    print("=== List of Pydantic Models (Tabular) ===")
    
    products = [
        Product(sku='LAP-001', name='Gaming Laptop', price=1299.99, stock=15, tags=['electronics', 'computers']),
        Product(sku='MOU-042', name='Wireless Mouse', price=29.99, stock=128, tags=['electronics', 'accessories']),
        Product(sku='KEY-789', name='Mechanical Keyboard', price=149.99, stock=67, tags=['electronics', 'accessories'])
    ]
    
    print("Python objects:")
    for p in products:
        print(f"  {p.sku}: {p.name} - ${p.price}")
    print()
    
    # Compare with regular dict encoding
    dict_data = {'products': [p.model_dump() if hasattr(p, 'model_dump') else p.dict() for p in products]}
    json_str = json.dumps(dict_data)
    toon_dict = encode(dict_data)
    toon_pydantic = encode_pydantic(products)
    
    print(f"JSON size: {len(json_str)} bytes")
    print(f"TOON size (from dict): {len(toon_dict)} bytes")
    print(f"TOON size (from pydantic): {len(toon_pydantic)} bytes")
    print()
    
    print("TOON format:")
    print(toon_pydantic)
    print()


def example_nested_models():
    """Example: Nested Pydantic models."""
    print("=== Nested Pydantic Models ===")
    
    user = User(
        id=2,
        name='Bob Johnson',
        email='bob@example.com',
        age=35,
        active=True,
        address=Address(
            street='123 Main Street',
            city='Boston',
            state='MA',
            zipcode='02101'
        )
    )
    
    toon = encode_pydantic(user)
    print("TOON format:")
    print(toon)
    print()


def example_exclude_options():
    """Example: Using exclude options."""
    print("=== Exclude Options ===")
    
    user = User(
        id=3,
        name='Charlie Brown',
        email='charlie@example.com'
        # age, active, and address use defaults or are None
    )
    
    print("All fields (default):")
    toon_all = encode_pydantic(user, exclude_unset=False)
    print(toon_all)
    print()
    
    print("Exclude unset fields:")
    toon_unset = encode_pydantic(user, exclude_unset=True)
    print(toon_unset)
    print()
    
    print("Exclude None values:")
    toon_none = encode_pydantic(user, exclude_none=True)
    print(toon_none)
    print()


def example_field_aliases():
    """Example: Using field aliases."""
    print("=== Field Aliases ===")
    
    order = Order(
        orderId='ORD-12345',
        customerName='Diana Prince',
        products=[
            Product(sku='LAP-001', name='Gaming Laptop', price=1299.99, stock=15),
            Product(sku='MOU-042', name='Wireless Mouse', price=29.99, stock=128)
        ],
        total=1329.98
    )
    
    print("Without aliases (internal field names):")
    toon_no_alias = encode_pydantic(order, by_alias=False)
    print(toon_no_alias)
    print()
    
    print("With aliases (API field names):")
    toon_alias = encode_pydantic(order, by_alias=True)
    print(toon_alias)
    print()


def example_decoding():
    """Example: Decoding TOON back to Pydantic models."""
    print("=== Decoding TOON to Pydantic ===")
    
    # TOON string representing a list of users
    toon = """[3]{id,name,email,age,active}:
  1,Alice Smith,alice@example.com,30,true
  2,Bob Johnson,bob@example.com,35,true
  3,Charlie Brown,charlie@example.com,28,false"""
    
    print("TOON input:")
    print(toon)
    print()
    
    # Decode to list of User objects
    users = decode_to_pydantic(toon, User)
    
    print("Decoded Pydantic models:")
    for user in users:
        print(f"  User(id={user.id}, name='{user.name}', age={user.age}, active={user.active})")
    print()


def example_roundtrip():
    """Example: Round-trip conversion."""
    print("=== Round-trip Conversion ===")
    
    original = [
        Product(sku='KEY-001', name='Wireless Keyboard', price=79.99, stock=45, tags=['wireless', 'keyboard']),
        Product(sku='MOU-002', name='Gaming Mouse', price=59.99, stock=78, tags=['gaming', 'mouse']),
    ]
    
    print("Original objects:")
    for p in original:
        print(f"  {p.sku}: {p.name} - ${p.price} (stock: {p.stock})")
    print()
    
    # Encode to TOON
    toon = encode_pydantic(original)
    print("TOON format:")
    print(toon)
    print()
    
    # Decode back to Pydantic
    decoded = decode_to_pydantic(toon, Product)
    print("Decoded objects:")
    for p in decoded:
        print(f"  {p.sku}: {p.name} - ${p.price} (stock: {p.stock})")
    print()
    
    # Verify equality
    print("Round-trip successful:", all(
        orig.sku == dec.sku and
        orig.name == dec.name and
        orig.price == dec.price and
        orig.stock == dec.stock
        for orig, dec in zip(original, decoded)
    ))
    print()


def example_comparison():
    """Example: Size comparison between JSON and TOON."""
    print("=== Size Comparison: JSON vs TOON ===")
    
    # Create a list of products
    products = [
        Product(sku=f'PROD-{i:03d}', name=f'Product {i}', price=float(10 + i), stock=100 - i)
        for i in range(1, 11)
    ]
    
    # Convert to JSON
    json_data = [p.model_dump() if hasattr(p, 'model_dump') else p.dict() for p in products]
    json_str = json.dumps(json_data)
    
    # Convert to TOON
    toon_str = encode_pydantic(products)
    
    print(f"Number of products: {len(products)}")
    print(f"JSON size: {len(json_str)} bytes")
    print(f"TOON size: {len(toon_str)} bytes")
    print(f"Size reduction: {100 - (len(toon_str) / len(json_str) * 100):.1f}%")
    print()
    
    print("JSON format (first 200 chars):")
    print(json_str[:200] + "...")
    print()
    
    print("TOON format:")
    print(toon_str)
    print()


if __name__ == '__main__':
    example_simple_model()
    example_list_of_models()
    example_nested_models()
    example_exclude_options()
    example_field_aliases()
    example_decoding()
    example_roundtrip()
    example_comparison()

