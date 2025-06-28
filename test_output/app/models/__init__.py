"""SQLAlchemy models and Pydantic schemas.

This module contains the database models and Pydantic schemas for the API.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# SQLAlchemy base class
Base = declarative_base()

# Type mapping from API spec types to Python types
TYPE_MAPPING = {
    'str': 'str',
    'int': 'int',
    'float': 'float',
    'bool': 'bool',
    'datetime': 'datetime',
    'date': 'date',
    'time': 'time',
    'json': 'Dict[str, Any]',
    'list': 'List[Any]',
    'url': 'HttpUrl',
}

# Default SQLAlchemy column types for each field type
DB_TYPE_MAPPING = {
    'str': 'String',
    'int': 'Integer',
    'float': 'Float',
    'bool': 'Boolean',
    'datetime': 'DateTime',
    'date': 'Date',
    'time': 'Time',
    'json': 'JSONB',
    'list': 'JSONB',
    'url': 'String',
}

# Pydantic models (schemas)



class ProductBase(BaseModel):
    """Base model for Product with common fields.
    
    Attributes:
    
        name: str - Required field
        price: float - Required field
        description: str - Optional field
    """
    
    name: str = None
    price: float = None
    description: str | None = None

    class Config:
        """Pydantic config for ProductBase."""
        orm_mode = True
        arbitrary_types_allowed = True


class ProductCreate(ProductBase):
    """Model for creating a new Product.
    
    Inherits all fields from ProductBase.
    """
    pass


class ProductUpdate(BaseModel):
    """Model for updating a Product.
    
    All fields are optional for partial updates.
    """
    
    name: str | None = None
    price: float | None = None
    description: str | None = None


class Product(ProductBase):
    """Complete Product model with ID and timestamps.
    
    Inherits all fields from ProductBase and adds:
        id: UUID - Primary key
        created_at: datetime - Creation timestamp
        updated_at: datetime - Last update timestamp
    """
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config for Product."""
        orm_mode = True
        arbitrary_types_allowed = True


class DBProduct(Base):
    """Database model for Product.
    
    This class represents the SQLAlchemy model for the Product entity.
    """
    __tablename__ = "product"
    
    # Primary key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    
    # Model fields
    name = Column(String, nullable=False)price = Column(Float, nullable=False)description = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        result = {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add model fields
        
        result["name"] = self.name
        result["price"] = self.price
        result["description"] = self.description
        
        return result
    
    def update(self, data: dict) -> None:
        """Update model fields from a dictionary.
        
        Args:
            data: Dictionary containing field names and values to update
        """
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

