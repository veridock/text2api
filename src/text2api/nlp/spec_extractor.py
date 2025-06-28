"""Module for extracting API specifications from natural language text using NLP."""
from typing import Dict, List, Optional, Any
import re
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

class SpecExtractor:
    """Extracts API specifications from natural language descriptions."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the spec extractor with a spaCy NLP model.
        
        Args:
            model_name: Name of the spaCy model to use for NLP processing
        """
        import spacy
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # If model is not found, download it
            import spacy.cli
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
        
        # Add custom pipeline components if they don't exist
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler")
            self._add_entity_patterns(ruler)
    
    def _add_entity_patterns(self, ruler):
        """Add patterns for entity recognition."""
        patterns = [
            # Domain-specific entities
            {"label": "DOMAIN", "pattern": [{"LOWER": "e-commerce"}]},
            {"label": "DOMAIN", "pattern": [{"LOWER": "ecommerce"}]},
            {"label": "DOMAIN", "pattern": [{"LOWER": "inventory"}]},
            {"label": "DOMAIN", "pattern": [{"LOWER": "warehouse"}]},
            
            # Common entities
            {"label": "RESOURCE", "pattern": [{"LOWER": "product"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "products"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "item"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "items"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "category"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "categories"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "machine"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "machines"}]},
            {"label": "RESOURCE", "pattern": [{"LOWER": "inventory"}]},
            
            # Common attributes
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "name"}]},
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "description"}]},
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "price"}]},
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "quantity"}]},
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "status"}]},
            {"label": "ATTRIBUTE", "pattern": [{"LOWER": "type"}]},
        ]
        ruler.add_patterns(patterns)
    
    def extract_spec(self, text: str) -> Dict[str, Any]:
        """Extract API specification from natural language text.
        
        Args:
            text: Natural language description of the API
            
        Returns:
            Dictionary containing the extracted API specification
        """
        doc = self.nlp(text)
        
        # Initialize the spec with default values
        spec = {
            "name": self._extract_api_name(text),
            "description": text.strip(),
            "models": self._extract_models(doc),
            "operations": self._extract_operations(doc),
            "domain": self._extract_domain(doc),
        }
        
        return spec
    
    def _extract_api_name(self, text: str) -> str:
        """Extract a name for the API from the input text."""
        # Use the first few words of the text as the name
        name = " ".join(text.split()[:5])
        # Remove any non-alphanumeric characters and trim
        name = re.sub(r'[^\w\s-]', '', name).strip()
        # Convert to CamelCase
        name = "".join(word.capitalize() for word in name.split())
        return name or "GeneratedAPI"
    
    def _extract_models(self, doc: Doc) -> List[Dict[str, Any]]:
        """Extract data models from the processed document."""
        models = []
        resources = []
        text = doc.text.lower()
        
        # Check for specific domains based on keywords
        if any(word in text for word in ["produkt", "sklep", "cena", "kategori"]):
            # E-commerce product management API
            models.append({
                "name": "Product",
                "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "price", "type": "float", "required": True},
                    {"name": "category_id", "type": "str", "required": True},
                    {"name": "stock_quantity", "type": "int", "required": True, "default": 0},
                    {"name": "is_active", "type": "bool", "required": True, "default": True},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]
            })
            models.append({
                "name": "Category",
                "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "parent_id", "type": "str", "required": False},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]
            })
        elif any(word in text for word in ["maszyna", "magazyn", "sprzęt", "urządzenie"]):
            # Warehouse equipment management API
            models.append({
                "name": "Machine",
                "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "model", "type": "str", "required": True},
                    {"name": "serial_number", "type": "str", "required": True, "unique": True},
                    {"name": "location", "type": "str", "required": True},
                    {"name": "status", "type": "str", "required": True, "default": "available"},
                    {"name": "last_maintenance_date", "type": "date", "required": False},
                    {"name": "next_maintenance_date", "type": "date", "required": False},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]
            })
            models.append({
                "name": "MaintenanceLog",
                "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "machine_id", "type": "str", "required": True},
                    {"name": "maintenance_type", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "technician", "type": "str", "required": True},
                    {"name": "completed_at", "type": "datetime", "required": True},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]
            })
        else:
            # Default generic API
            models.append({
                "name": "Item",
                "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]
            })
        
        return models
    
    def _extract_operations(self, doc: Doc) -> List[str]:
        """Extract supported operations from the document."""
        # Default operations for REST APIs
        operations = ["create", "read", "update", "delete", "list"]
        
        # Check for specific operations mentioned in the text
        text = doc.text.lower()
        
        if "list" in text or "get all" in text:
            operations.append("list")
        if "create" in text or "add" in text or "new" in text:
            operations.append("create")
        if "read" in text or "get" in text or "fetch" in text:
            operations.append("read")
        if "update" in text or "modify" in text or "change" in text:
            operations.append("update")
        if "delete" in text or "remove" in text or "erase" in text:
            operations.append("delete")
        
        return list(dict.fromkeys(operations))  # Remove duplicates while preserving order
    
    def _extract_domain(self, doc: Doc) -> str:
        """Extract the domain from the document."""
        # Look for domain entities
        domains = [ent.text for ent in doc.ents if ent.label_ == "DOMAIN"]
        
        if domains:
            return domains[0].lower()
        
        # Infer domain from text
        text = doc.text.lower()
        if any(word in text for word in ["shop", "store", "product", "ecommerce"]):
            return "ecommerce"
        elif any(word in text for word in ["inventory", "warehouse", "stock"]):
            return "inventory"
        elif any(word in text for word in ["machine", "equipment", "device"]):
            return "industrial"
        
        return "general"


def extract_spec(text: str) -> Dict[str, Any]:
    """Convenience function to extract API spec from text."""
    extractor = SpecExtractor()
    return extractor.extract_spec(text)
