"""Tests for Pydantic model conversion."""
import pytest

# Check if pydantic is available
try:
    from pydantic import BaseModel, Field
    from toon import encode_pydantic, decode_to_pydantic
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="pydantic not installed")
class TestPydanticEncoder:
    """Tests for encode_pydantic function."""
    
    def test_simple_model(self):
        """Test encoding a simple Pydantic model."""
        class User(BaseModel):
            id: int
            name: str
            email: str
        
        user = User(id=1, name='Alice', email='alice@example.com')
        toon = encode_pydantic(user)
        
        assert 'id: 1' in toon
        assert 'name: Alice' in toon
        assert 'email: alice@example.com' in toon
    
    def test_list_of_models_tabular(self):
        """Test encoding a list of uniform Pydantic models (tabular format)."""
        class Product(BaseModel):
            sku: str
            name: str
            price: float
        
        products = [
            Product(sku='LAP-001', name='Gaming Laptop', price=1299.99),
            Product(sku='MOU-042', name='Wireless Mouse', price=29.99)
        ]
        
        toon = encode_pydantic(products)
        
        # Should use tabular format
        assert '[2]{sku,name,price}:' in toon
        assert 'LAP-001,Gaming Laptop,1299.99' in toon
        assert 'MOU-042,Wireless Mouse,29.99' in toon
    
    def test_nested_models(self):
        """Test encoding nested Pydantic models."""
        class Address(BaseModel):
            street: str
            city: str
            zipcode: str
        
        class Person(BaseModel):
            name: str
            age: int
            address: Address
        
        person = Person(
            name='Bob',
            age=35,
            address=Address(street='123 Main St', city='Boston', zipcode='02101')
        )
        
        toon = encode_pydantic(person)
        
        assert 'name: Bob' in toon
        assert 'age: 35' in toon
        assert 'address:' in toon
        assert 'street: 123 Main St' in toon
        assert 'city: Boston' in toon
        assert 'zipcode: 02101' in toon
    
    def test_exclude_unset(self):
        """Test excluding unset fields."""
        class Config(BaseModel):
            host: str
            port: int = 8080
            debug: bool = False
        
        config = Config(host='localhost')
        
        # With exclude_unset=False (default)
        toon_all = encode_pydantic(config, exclude_unset=False)
        assert 'port: 8080' in toon_all
        assert 'debug: false' in toon_all
        
        # With exclude_unset=True
        toon_set = encode_pydantic(config, exclude_unset=True)
        assert 'host: localhost' in toon_set
        assert 'port' not in toon_set
        assert 'debug' not in toon_set
    
    def test_exclude_none(self):
        """Test excluding None values."""
        class User(BaseModel):
            id: int
            name: str
            email: str | None = None  # Use | syntax for Python 3.10+
        
        user = User(id=1, name='Alice', email=None)
        
        # With exclude_none=False (default)
        toon_all = encode_pydantic(user, exclude_none=False)
        assert 'email: null' in toon_all
        
        # With exclude_none=True
        toon_no_none = encode_pydantic(user, exclude_none=True)
        assert 'email' not in toon_no_none
    
    def test_by_alias(self):
        """Test using field aliases."""
        class User(BaseModel):
            user_id: int = Field(alias='id')
            user_name: str = Field(alias='name')
        
        user = User(id=1, name='Alice')
        
        # Without alias
        toon_no_alias = encode_pydantic(user, by_alias=False)
        assert 'user_id: 1' in toon_no_alias
        assert 'user_name: Alice' in toon_no_alias
        
        # With alias
        toon_alias = encode_pydantic(user, by_alias=True)
        assert 'id: 1' in toon_alias
        assert 'name: Alice' in toon_alias
    
    def test_with_encoding_options(self):
        """Test encoding with custom TOON options."""
        class Item(BaseModel):
            id: int
            tags: list[str]
        
        item = Item(id=1, tags=['tag1', 'tag2', 'tag3'])
        
        # Tab delimiter
        toon_tab = encode_pydantic(item, options={'delimiter': 'tab'})
        assert 'tags: [tag1\ttag2\ttag3]' in toon_tab
        
        # Pipe delimiter
        toon_pipe = encode_pydantic(item, options={'delimiter': 'pipe'})
        assert 'tags: [tag1|tag2|tag3]' in toon_pipe
    
    def test_invalid_input(self):
        """Test error handling for invalid input."""
        with pytest.raises(ValueError, match="Expected Pydantic BaseModel"):
            encode_pydantic({'not': 'a model'})
        
        with pytest.raises(ValueError, match="Expected Pydantic BaseModel"):
            encode_pydantic("string")


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="pydantic not installed")
class TestPydanticDecoder:
    """Tests for decode_to_pydantic function."""
    
    def test_decode_simple_model(self):
        """Test decoding TOON to a simple Pydantic model."""
        class User(BaseModel):
            id: int
            name: str
            email: str
        
        toon = """id: 1
name: Alice
email: alice@example.com"""
        
        user = decode_to_pydantic(toon, User)
        
        assert isinstance(user, User)
        assert user.id == 1
        assert user.name == 'Alice'
        assert user.email == 'alice@example.com'
    
    def test_decode_list_of_models(self):
        """Test decoding TOON to a list of Pydantic models."""
        class Product(BaseModel):
            sku: str
            name: str
            price: float
        
        toon = """[2]{sku,name,price}:
  LAP-001,Gaming Laptop,1299.99
  MOU-042,Wireless Mouse,29.99"""
        
        products = decode_to_pydantic(toon, Product)
        
        assert isinstance(products, list)
        assert len(products) == 2
        assert all(isinstance(p, Product) for p in products)
        assert products[0].sku == 'LAP-001'
        assert products[0].name == 'Gaming Laptop'
        assert products[0].price == 1299.99
        assert products[1].sku == 'MOU-042'
    
    def test_decode_nested_models(self):
        """Test decoding nested Pydantic models."""
        class Address(BaseModel):
            street: str
            city: str
            zipcode: str
        
        class Person(BaseModel):
            name: str
            age: int
            address: Address
        
        toon = """name: Bob
age: 35
address:
  street: 123 Main St
  city: Boston
  zipcode: "02101\""""
        
        person = decode_to_pydantic(toon, Person)
        
        assert isinstance(person, Person)
        assert person.name == 'Bob'
        assert person.age == 35
        assert isinstance(person.address, Address)
        assert person.address.street == '123 Main St'
        assert person.address.city == 'Boston'
        assert person.address.zipcode == '02101'
    
    def test_decode_with_validation(self):
        """Test that Pydantic validation works during decoding."""
        class User(BaseModel):
            id: int
            age: int
        
        # Valid data
        toon_valid = """id: 1
age: 25"""
        user = decode_to_pydantic(toon_valid, User)
        assert user.id == 1
        assert user.age == 25
        
        # Invalid data (string for int field)
        toon_invalid = """id: 1
age: not_a_number"""
        
        with pytest.raises(Exception):  # Pydantic validation error
            decode_to_pydantic(toon_invalid, User)
    
    def test_invalid_model_class(self):
        """Test error handling for invalid model class."""
        with pytest.raises(ValueError, match="Expected Pydantic BaseModel class"):
            decode_to_pydantic("data: value", dict)
        
        with pytest.raises(ValueError, match="Expected Pydantic BaseModel class"):
            decode_to_pydantic("data: value", "not a class")
    
    def test_roundtrip(self):
        """Test encoding and decoding round-trip."""
        class User(BaseModel):
            id: int
            name: str
            email: str
            active: bool
        
        original = User(id=42, name='Charlie', email='charlie@example.com', active=True)
        
        # Encode to TOON
        toon = encode_pydantic(original)
        
        # Decode back to Pydantic
        decoded = decode_to_pydantic(toon, User)
        
        # Verify equality
        assert decoded.id == original.id
        assert decoded.name == original.name
        assert decoded.email == original.email
        assert decoded.active == original.active
    
    def test_list_roundtrip(self):
        """Test encoding and decoding round-trip with list."""
        class Item(BaseModel):
            id: int
            name: str
            price: float
        
        original = [
            Item(id=1, name='Item 1', price=19.99),
            Item(id=2, name='Item 2', price=29.99),
            Item(id=3, name='Item 3', price=39.99)
        ]
        
        # Encode to TOON
        toon = encode_pydantic(original)
        
        # Decode back to Pydantic
        decoded = decode_to_pydantic(toon, Item)
        
        # Verify equality
        assert len(decoded) == len(original)
        for orig, dec in zip(original, decoded):
            assert dec.id == orig.id
            assert dec.name == orig.name
            assert dec.price == orig.price


@pytest.mark.skipif(PYDANTIC_AVAILABLE, reason="test for when pydantic is not installed")
def test_pydantic_not_installed():
    """Test that appropriate error is raised when pydantic is not installed."""
    from toon import encode_pydantic, decode_to_pydantic
    
    # When pydantic is not installed, these should be None
    assert encode_pydantic is None
    assert decode_to_pydantic is None

