"""Factory for creating generators."""
from typing import Optional, Type, Dict, Any

from .base_generator import BaseGenerator
from .openapi_generator import OpenAPIGenerator
from .fastapi_generator import FastAPIGenerator
from .client_generator import ClientGenerator


class GeneratorFactory:
    """Factory class for creating different types of generators."""
    
    GENERATORS = {
        'openapi': OpenAPIGenerator,
        'fastapi': FastAPIGenerator,
        'client': ClientGenerator,
    }
    
    @classmethod
    def create_generator(
        cls,
        generator_type: str,
        output_dir: str = "generated_apis",
        **kwargs
    ) -> BaseGenerator:
        """Create a generator of the specified type.
        
        Args:
            generator_type: Type of generator to create (openapi, fastapi, client)
            output_dir: Base directory where generated files will be saved
            **kwargs: Additional keyword arguments to pass to the generator
            
        Returns:
            An instance of the specified generator type
            
        Raises:
            ValueError: If the specified generator type is not supported
        """
        generator_class = cls.GENERATORS.get(generator_type.lower())
        if not generator_class:
            raise ValueError(
                f"Unknown generator type: {generator_type}. "
                f"Available types: {', '.join(cls.GENERATORS.keys())}"
            )
            
        return generator_class(output_dir=output_dir, **kwargs)
    
    @classmethod
    def get_available_generators(cls) -> Dict[str, Type[BaseGenerator]]:
        """Get a dictionary of available generator types and their classes.
        
        Returns:
            Dict mapping generator type names to their classes
        """
        return cls.GENERATORS.copy()
