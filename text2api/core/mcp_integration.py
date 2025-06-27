"""
Model Context Protocol (MCP) integration for enhanced API generation
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .analyzer import ApiSpec, Endpoint, Field


class MCPIntegration:
    """Integracja z Model Context Protocol dla zaawansowanej analizy"""

    def __init__(self, mcp_server_url: Optional[str] = None):
        self.mcp_server_url = mcp_server_url or "http://localhost:8765"
        self.enabled = False
        self.capabilities = []

    async def initialize(self) -> bool:
        """Inicjalizuje połączenie z MCP server"""
        try:
            # Sprawdź czy MCP server jest dostępny
            # W rzeczywistej implementacji byłoby to rzeczywiste połączenie
            self.enabled = await self._check_mcp_availability()
            if self.enabled:
                self.capabilities = await self._get_mcp_capabilities()
            return self.enabled
        except Exception as e:
            print(f"MCP initialization failed: {e}")
            return False

    async def _check_mcp_availability(self) -> bool:
        """Sprawdza dostępność MCP server"""
        # Symulacja sprawdzenia - w rzeczywistości byłoby to prawdziwe połączenie
        return False  # Wyłączone domyślnie

    async def _get_mcp_capabilities(self) -> List[str]:
        """Pobiera capabilities z MCP server"""
        return [
            "enhanced_nlp_analysis",
            "domain_specific_templates",
            "code_generation_optimization",
            "security_pattern_detection",
            "performance_recommendations",
        ]

    async def enhance_spec(self, api_spec: ApiSpec) -> ApiSpec:
        """Wzbogaca specyfikację API używając MCP"""

        if not self.enabled:
            return api_spec

        try:
            # Enhanced NLP analysis
            if "enhanced_nlp_analysis" in self.capabilities:
                api_spec = await self._enhance_nlp_analysis(api_spec)

            # Domain-specific templates
            if "domain_specific_templates" in self.capabilities:
                api_spec = await self._apply_domain_templates(api_spec)

            # Security patterns
            if "security_pattern_detection" in self.capabilities:
                api_spec = await self._enhance_security(api_spec)

            # Performance optimization
            if "performance_recommendations" in self.capabilities:
                api_spec = await self._optimize_performance(api_spec)

            return api_spec

        except Exception as e:
            print(f"MCP enhancement failed: {e}")
            return api_spec

    async def _enhance_nlp_analysis(self, api_spec: ApiSpec) -> ApiSpec:
        """Ulepsza analizę NLP używając MCP"""

        # Symulacja - w rzeczywistości używałby MCP dla zaawansowanej analizy
        enhancements = {
            "entity_relationships": self._detect_entity_relationships(api_spec),
            "business_rules": self._extract_business_rules(api_spec),
            "data_flow": self._analyze_data_flow(api_spec),
        }

        # Dodaj wykryte związki między encjami
        if enhancements["entity_relationships"]:
            api_spec = self._add_entity_relationships(
                api_spec, enhancements["entity_relationships"]
            )

        return api_spec

    def _detect_entity_relationships(self, api_spec: ApiSpec) -> Dict[str, List[str]]:
        """Wykrywa związki między encjami"""

        relationships = {}

        # Analiza nazw endpointów i modeli
        for model in api_spec.models:
            model_name = model["name"].lower()
            related_entities = []

            # Szukaj powiązań w innych modelach
            for other_model in api_spec.models:
                if other_model["name"] != model["name"]:
                    other_name = other_model["name"].lower()

                    # Sprawdź czy nazwy sugerują związek
                    if any(
                        field["name"].endswith("_id") and other_name in field["name"]
                        for field in model.get("fields", [])
                    ):
                        related_entities.append(other_model["name"])

            if related_entities:
                relationships[model["name"]] = related_entities

        return relationships

    def _extract_business_rules(self, api_spec: ApiSpec) -> List[str]:
        """Ekstraktuje reguły biznesowe z opisu"""

        rules = []
        description = api_spec.description.lower()

        # Wzorce dla typowych reguł biznesowych
        rule_patterns = [
            ("authentication", r"login|register|auth|token"),
            ("authorization", r"permission|role|admin|access"),
            ("validation", r"valid|check|verify|confirm"),
            ("workflow", r"approve|reject|pending|status"),
            ("audit", r"log|track|history|audit"),
        ]

        for rule_type, pattern in rule_patterns:
            import re

            if re.search(pattern, description):
                rules.append(rule_type)

        return rules

    def _analyze_data_flow(self, api_spec: ApiSpec) -> Dict[str, Any]:
        """Analizuje przepływ danych"""

        flow = {
            "input_endpoints": [],
            "output_endpoints": [],
            "processing_endpoints": [],
        }

        for endpoint in api_spec.endpoints:
            if endpoint.method.value in ["POST", "PUT", "PATCH"]:
                flow["input_endpoints"].append(endpoint.name)
            elif endpoint.method.value == "GET":
                flow["output_endpoints"].append(endpoint.name)
            else:
                flow["processing_endpoints"].append(endpoint.name)

        return flow

    def _add_entity_relationships(
        self, api_spec: ApiSpec, relationships: Dict[str, List[str]]
    ) -> ApiSpec:
        """Dodaje związki między encjami do modeli"""

        for model in api_spec.models:
            model_name = model["name"]
            if model_name in relationships:
                # Dodaj foreign key fields
                for related_entity in relationships[model_name]:
                    fk_field = {
                        "name": f"{related_entity.lower()}_id",
                        "type": "integer",
                        "required": False,
                        "description": f"Reference to {related_entity}",
                    }

                    # Sprawdź czy pole już nie istnieje
                    existing_fields = [f["name"] for f in model.get("fields", [])]
                    if fk_field["name"] not in existing_fields:
                        model.setdefault("fields", []).append(fk_field)

        return api_spec

    async def _apply_domain_templates(self, api_spec: ApiSpec) -> ApiSpec:
        """Stosuje szablony specyficzne dla domeny"""

        domain_keywords = {
            "ecommerce": ["product", "order", "cart", "payment", "customer"],
            "blog": ["post", "comment", "tag", "author", "category"],
            "cms": ["content", "page", "article", "media", "user"],
            "crm": ["customer", "lead", "contact", "deal", "company"],
            "hrm": ["employee", "department", "position", "salary", "leave"],
        }

        detected_domain = self._detect_domain(api_spec, domain_keywords)

        if detected_domain:
            api_spec = await self._apply_domain_enhancements(api_spec, detected_domain)

        return api_spec

    def _detect_domain(
        self, api_spec: ApiSpec, domain_keywords: Dict[str, List[str]]
    ) -> Optional[str]:
        """Wykrywa domenę aplikacji"""

        text = (
            f"{api_spec.description} {' '.join([m['name'] for m in api_spec.models])}"
        )
        text_lower = text.lower()

        domain_scores = {}

        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)

        return None

    async def _apply_domain_enhancements(
        self, api_spec: ApiSpec, domain: str
    ) -> ApiSpec:
        """Stosuje ulepszenia specyficzne dla domeny"""

        domain_enhancements = {
            "ecommerce": {
                "additional_endpoints": [
                    {
                        "path": "/cart/add",
                        "method": "POST",
                        "name": "add_to_cart",
                        "description": "Add item to shopping cart",
                    },
                    {
                        "path": "/orders/{id}/status",
                        "method": "PUT",
                        "name": "update_order_status",
                        "description": "Update order status",
                    },
                ],
                "required_auth": True,
                "database_required": True,
            },
            "blog": {
                "additional_endpoints": [
                    {
                        "path": "/posts/{id}/comments",
                        "method": "GET",
                        "name": "get_post_comments",
                        "description": "Get comments for a post",
                    }
                ],
                "auth_type": "jwt",
            },
        }

        if domain in domain_enhancements:
            enhancements = domain_enhancements[domain]

            # Dodaj dodatkowe endpointy
            if "additional_endpoints" in enhancements:
                for ep_data in enhancements["additional_endpoints"]:
                    # Sprawdź czy endpoint już nie istnieje
                    existing_paths = [ep.path for ep in api_spec.endpoints]
                    if ep_data["path"] not in existing_paths:
                        from .analyzer import HttpMethod

                        new_endpoint = Endpoint(
                            path=ep_data["path"],
                            method=HttpMethod(ep_data["method"]),
                            name=ep_data["name"],
                            description=ep_data["description"],
                            parameters=[],
                        )
                        api_spec.endpoints.append(new_endpoint)

            # Aktualizuj wymagania
            if "required_auth" in enhancements and enhancements["required_auth"]:
                api_spec.auth_type = api_spec.auth_type or "jwt"

            if "database_required" in enhancements:
                api_spec.database_required = enhancements["database_required"]

        return api_spec

    async def _enhance_security(self, api_spec: ApiSpec) -> ApiSpec:
        """Dodaje wzorce bezpieczeństwa"""

        # Wykryj potrzeby bezpieczeństwa
        security_needs = self._analyze_security_needs(api_spec)

        # Dodaj odpowiednie zabezpieczenia
        if "authentication" in security_needs:
            api_spec.auth_type = api_spec.auth_type or "jwt"

        if "data_protection" in security_needs:
            # Dodaj pola związane z GDPR/privacy
            for model in api_spec.models:
                if any(
                    field["name"] in ["email", "phone", "name"]
                    for field in model.get("fields", [])
                ):
                    privacy_fields = [
                        {
                            "name": "privacy_consent",
                            "type": "boolean",
                            "required": False,
                            "description": "User privacy consent status",
                        },
                        {
                            "name": "data_retention_date",
                            "type": "datetime",
                            "required": False,
                            "description": "Data retention expiry date",
                        },
                    ]

                    existing_fields = [f["name"] for f in model.get("fields", [])]
                    for field in privacy_fields:
                        if field["name"] not in existing_fields:
                            model.setdefault("fields", []).append(field)

        return api_spec

    def _analyze_security_needs(self, api_spec: ApiSpec) -> List[str]:
        """Analizuje potrzeby bezpieczeństwa"""

        needs = []
        description_lower = api_spec.description.lower()

        # Sprawdź różne wzorce bezpieczeństwa
        if any(
            word in description_lower
            for word in ["user", "login", "account", "profile"]
        ):
            needs.append("authentication")

        if any(
            word in description_lower
            for word in ["personal", "private", "sensitive", "gdpr"]
        ):
            needs.append("data_protection")

        if any(
            word in description_lower
            for word in ["payment", "transaction", "money", "billing"]
        ):
            needs.append("financial_security")

        if any(
            word in description_lower
            for word in ["admin", "manage", "control", "moderate"]
        ):
            needs.append("authorization")

        return needs

    async def _optimize_performance(self, api_spec: ApiSpec) -> ApiSpec:
        """Dodaje optymalizacje wydajności"""

        # Analiza potencjalnych problemów wydajności
        performance_issues = self._analyze_performance_needs(api_spec)

        # Dodaj odpowiednie optymalizacje
        if "caching" in performance_issues:
            # Dodaj cache headers do endpointów GET
            for endpoint in api_spec.endpoints:
                if endpoint.method.value == "GET":
                    endpoint.description += " (with caching)"

        if "pagination" in performance_issues:
            # Dodaj parametry paginacji do endpointów listujących
            for endpoint in api_spec.endpoints:
                if "list" in endpoint.name or endpoint.path.count("/") == 1:
                    pagination_params = [
                        Field(name="page", type="integer", required=False, default=1),
                        Field(name="limit", type="integer", required=False, default=20),
                    ]

                    existing_params = [p.name for p in endpoint.parameters]
                    for param in pagination_params:
                        if param.name not in existing_params:
                            endpoint.parameters.append(param)

        return api_spec

    def _analyze_performance_needs(self, api_spec: ApiSpec) -> List[str]:
        """Analizuje potrzeby wydajności"""

        needs = []

        # Sprawdź czy są endpointy do listowania
        has_list_endpoints = any("list" in ep.name for ep in api_spec.endpoints)
        if has_list_endpoints:
            needs.append("pagination")

        # Sprawdź czy są endpointy GET (mogą korzystać z cache)
        has_get_endpoints = any(ep.method.value == "GET" for ep in api_spec.endpoints)
        if has_get_endpoints:
            needs.append("caching")

        # Sprawdź czy jest dużo modeli (może potrzebować optymalizacji DB)
        if len(api_spec.models) > 3:
            needs.append("database_optimization")

        return needs

    async def get_enhancement_report(
        self, original_spec: ApiSpec, enhanced_spec: ApiSpec
    ) -> Dict[str, Any]:
        """Generuje raport z ulepszeń wprowadzonych przez MCP"""

        report = {
            "enhancements_applied": [],
            "endpoints_added": 0,
            "fields_added": 0,
            "security_improvements": [],
            "performance_optimizations": [],
            "original_endpoints": len(original_spec.endpoints),
            "enhanced_endpoints": len(enhanced_spec.endpoints),
            "original_models": len(original_spec.models),
            "enhanced_models": len(enhanced_spec.models),
        }

        # Porównaj endpointy
        original_paths = {ep.path for ep in original_spec.endpoints}
        enhanced_paths = {ep.path for ep in enhanced_spec.endpoints}
        new_paths = enhanced_paths - original_paths

        report["endpoints_added"] = len(new_paths)
        if new_paths:
            report["enhancements_applied"].append(
                f"Added {len(new_paths)} new endpoints"
            )

        # Porównaj modele
        original_model_fields = sum(
            len(m.get("fields", [])) for m in original_spec.models
        )
        enhanced_model_fields = sum(
            len(m.get("fields", [])) for m in enhanced_spec.models
        )
        fields_added = enhanced_model_fields - original_model_fields

        report["fields_added"] = fields_added
        if fields_added > 0:
            report["enhancements_applied"].append(f"Added {fields_added} model fields")

        # Sprawdź ulepszenia bezpieczeństwa
        if enhanced_spec.auth_type and not original_spec.auth_type:
            report["security_improvements"].append("Added authentication")

        # Sprawdź optymalizacje wydajności
        enhanced_pagination = any(
            "page" in [p.name for p in ep.parameters] for ep in enhanced_spec.endpoints
        )
        original_pagination = any(
            "page" in [p.name for p in ep.parameters] for ep in original_spec.endpoints
        )

        if enhanced_pagination and not original_pagination:
            report["performance_optimizations"].append("Added pagination support")

        return report

    def is_available(self) -> bool:
        """Sprawdza czy MCP jest dostępne"""
        return self.enabled

    def get_capabilities(self) -> List[str]:
        """Zwraca listę dostępnych capabilities"""
        return self.capabilities.copy() if self.enabled else []
