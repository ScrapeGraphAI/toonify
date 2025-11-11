"""Pydantic model converter for TOON format."""
from typing import Any, Dict, List, Optional, Union
from .encoder import encode, EncoderOptions


def encode_pydantic(
    model: Any,
    options: Optional[Dict[str, Any]] = None,
    exclude_unset: bool = False,
    exclude_none: bool = False,
    exclude_defaults: bool = False,
    by_alias: bool = False
) -> str:
    """
    Encode a Pydantic model to TOON format.
    
    This function converts Pydantic models (v1 or v2) to TOON format by first
    converting them to dictionaries and then encoding to TOON.
    
    Args:
        model: Pydantic model instance or list of model instances
        options: Encoding options (same as `encode` function)
            - delimiter: ',' (default), '\t', or '|'
            - indent: int (default 2)
            - key_folding: 'off' (default) or 'safe'
            - flatten_depth: int or None
        exclude_unset: If True, exclude fields that were not explicitly set
        exclude_none: If True, exclude fields with None values
        exclude_defaults: If True, exclude fields with default values
        by_alias: If True, use field aliases instead of field names
            
    Returns:
        TOON formatted string
        
    Raises:
        ImportError: If pydantic is not installed
        ValueError: If the model is not a valid Pydantic model
        
    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>> 
        >>> users = [
        ...     User(id=1, name='Alice', email='alice@example.com'),
        ...     User(id=2, name='Bob', email='bob@example.com')
        ... ]
        >>> print(encode_pydantic(users))
        [2]{id,name,email}:
          1,Alice,alice@example.com
          2,Bob,bob@example.com
    """
    try:
        from pydantic import BaseModel
    except ImportError:
        raise ImportError(
            "pydantic is required for encode_pydantic(). "
            "Install it with: pip install pydantic"
        )
    
    # Convert model(s) to dict
    data = _pydantic_to_dict(
        model,
        exclude_unset=exclude_unset,
        exclude_none=exclude_none,
        exclude_defaults=exclude_defaults,
        by_alias=by_alias
    )
    
    # Encode to TOON
    return encode(data, options)


def _pydantic_to_dict(
    model: Any,
    exclude_unset: bool = False,
    exclude_none: bool = False,
    exclude_defaults: bool = False,
    by_alias: bool = False
) -> Union[Dict, List]:
    """
    Convert Pydantic model(s) to dictionary/list.
    
    Supports both Pydantic v1 and v2.
    """
    try:
        from pydantic import BaseModel
    except ImportError:
        raise ImportError("pydantic is not installed")
    
    # Handle list of models
    if isinstance(model, list):
        return [
            _pydantic_to_dict(
                item,
                exclude_unset=exclude_unset,
                exclude_none=exclude_none,
                exclude_defaults=exclude_defaults,
                by_alias=by_alias
            )
            for item in model
        ]
    
    # Verify it's a Pydantic model
    if not isinstance(model, BaseModel):
        raise ValueError(
            f"Expected Pydantic BaseModel instance, got {type(model).__name__}"
        )
    
    # Try Pydantic v2 first, fall back to v1
    try:
        # Pydantic v2
        return model.model_dump(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
            mode='python'
        )
    except AttributeError:
        # Pydantic v1
        return model.dict(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias
        )


def decode_to_pydantic(toon_string: str, model_class: type, options: Optional[Dict[str, Any]] = None) -> Any:
    """
    Decode TOON string to Pydantic model(s).
    
    Args:
        toon_string: TOON formatted string
        model_class: Pydantic model class to instantiate
        options: Decoding options (same as `decode` function)
            - strict: bool (default True) - validate structure
            - expand_paths: 'off' (default) or 'safe'
            - default_delimiter: ',' (default)
            
    Returns:
        Pydantic model instance or list of instances
        
    Raises:
        ImportError: If pydantic is not installed
        ValueError: If model_class is not a valid Pydantic model class
        
    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>> 
        >>> toon = '''[2]{id,name,email}:
        ...   1,Alice,alice@example.com
        ...   2,Bob,bob@example.com'''
        >>> users = decode_to_pydantic(toon, User)
        >>> print(users[0].name)
        Alice
    """
    try:
        from pydantic import BaseModel
    except ImportError:
        raise ImportError(
            "pydantic is required for decode_to_pydantic(). "
            "Install it with: pip install pydantic"
        )
    
    from .decoder import decode
    
    # Verify model_class is a Pydantic model
    if not (isinstance(model_class, type) and issubclass(model_class, BaseModel)):
        raise ValueError(
            f"Expected Pydantic BaseModel class, got {type(model_class).__name__}"
        )
    
    # Decode TOON to dict/list
    data = decode(toon_string, options)
    
    # Convert to Pydantic model(s)
    if isinstance(data, list):
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("All items in the decoded list must be dicts to convert to Pydantic models")
        return [model_class(**item) for item in data]
    elif isinstance(data, dict):
        return model_class(**data)
    else:
        raise ValueError(f"Cannot convert {type(data).__name__} to Pydantic model")

