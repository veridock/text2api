"""Generators for text2api."""

from typing import Optional, Type, Dict, Any
from .base_generator import BaseGenerator
from .openapi_generator import OpenAPIGenerator
from .fastapi_generator import FastAPIGenerator
from .client_generator import ClientGenerator


class GeneratorFactory:
    """Factory class for creating generator instances based on generator type."""
    
    GENERATOR_MAP = {
        'openapi': OpenAPIGenerator,
        'fastapi': FastAPIGenerator,
        'client': ClientGenerator,
    }
    
    @classmethod
    def create_generator(
        cls, 
        generator_type: str, 
        output_dir: str = 'generated_apis',
        **kwargs
    ) -> Optional[BaseGenerator]:
        """Create a generator instance based on the generator type.
        
        Args:
            generator_type: Type of generator to create (openapi, fastapi, client)
            output_dir: Output directory for generated files
            **kwargs: Additional keyword arguments to pass to the generator
            
        Returns:
            Generator instance or None if generator type is not found
        """
        generator_class = cls.GENERATOR_MAP.get(generator_type.lower())
        if not generator_class:
            return None
            
        return generator_class(output_dir=output_dir, **kwargs)
    
    @classmethod
    def get_available_generators(cls) -> Dict[str, Type[BaseGenerator]]:
        """Get a dictionary of available generator types and their classes."""
        return dict(cls.GENERATOR_MAP)


__all__ = [
    'BaseGenerator',
    'OpenAPIGenerator',
    'FastAPIGenerator',
    'ClientGenerator',
    'GeneratorFactory',
]