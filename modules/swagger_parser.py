"""
Swagger/OpenAPI specification parser for API testing suite.
"""

import yaml
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import jsonschema
from jsonschema import validate, ValidationError


class SwaggerParser:
    """Parser for Swagger/OpenAPI specifications."""
    
    def __init__(self):
        self.spec = None
        self.base_url = None
        self.version = None
    
    def parse(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a Swagger/OpenAPI specification.
        
        Args:
            content: The parsed YAML/JSON content of the specification
            
        Returns:
            Parsed and validated specification
        """
        self.spec = content
        
        # Validate basic structure
        if not self._validate_spec():
            raise ValueError("Invalid OpenAPI/Swagger specification")
        
        # Extract version and base URL
        self.version = self._get_openapi_version()
        self.base_url = self._extract_base_url()
        
        # Normalize the specification
        normalized_spec = self._normalize_spec()
        
        # Parse security schemes
        normalized_spec['security_schemes'] = self._parse_security_schemes()
        
        return normalized_spec
    
    def _validate_spec(self) -> bool:
        """Validate the basic structure of the specification."""
        required_fields = ['paths']
        
        if not isinstance(self.spec, dict):
            return False
        
        for field in required_fields:
            if field not in self.spec:
                return False
        
        return True
    
    def _get_openapi_version(self) -> str:
        """Determine the OpenAPI/Swagger version."""
        if 'openapi' in self.spec:
            return self.spec['openapi']
        elif 'swagger' in self.spec:
            return self.spec['swagger']
        else:
            return '3.0.0'  # Default assumption
    
    def _extract_base_url(self) -> str:
        """Extract the base URL from the specification."""
        # OpenAPI 3.0+
        if 'servers' in self.spec and self.spec['servers']:
            return self.spec['servers'][0]['url']
        
        # Swagger 2.0
        if 'host' in self.spec:
            scheme = self.spec.get('schemes', ['http'])[0]
            host = self.spec['host']
            base_path = self.spec.get('basePath', '')
            return f"{scheme}://{host}{base_path}"
        
        return 'http://localhost'  # Default fallback
    
    def _normalize_spec(self) -> Dict[str, Any]:
        """Normalize the specification to a consistent format."""
        normalized = {
            'info': self.spec.get('info', {}),
            'servers': self._normalize_servers(),
            'paths': self._normalize_paths(),
            'components': self.spec.get('components', {}),
            'definitions': self.spec.get('definitions', {}),  # Swagger 2.0
            'version': self.version,
            'base_url': self.base_url
        }
        
        return normalized
    
    def _normalize_servers(self) -> List[Dict[str, Any]]:
        """Normalize server information."""
        if 'servers' in self.spec:
            return self.spec['servers']
        
        # Convert Swagger 2.0 format
        servers = []
        if 'host' in self.spec:
            scheme = self.spec.get('schemes', ['http'])[0]
            host = self.spec['host']
            base_path = self.spec.get('basePath', '')
            servers.append({
                'url': f"{scheme}://{host}{base_path}",
                'description': 'Default server'
            })
        
        return servers
    
    def _normalize_paths(self) -> Dict[str, Any]:
        """Normalize path definitions."""
        normalized_paths = {}
        
        for path, methods in self.spec.get('paths', {}).items():
            normalized_methods = {}
            
            for method, operation in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    normalized_methods[method.lower()] = self._normalize_operation(operation)
            
            if normalized_methods:
                normalized_paths[path] = normalized_methods
        
        return normalized_paths
    
    def _normalize_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize an individual operation."""
        return {
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'parameters': self._normalize_parameters(operation.get('parameters', [])),
            'requestBody': self._normalize_request_body(operation.get('requestBody')),
            'responses': operation.get('responses', {}),
            'tags': operation.get('tags', []),
            'operationId': operation.get('operationId', ''),
            'security': operation.get('security', [])
        }
    
    def _normalize_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize parameter definitions."""
        normalized = []
        
        for param in parameters:
            normalized_param = {
                'name': param.get('name', ''),
                'in': param.get('in', 'query'),
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', param.get('type', 'string')),
                'example': param.get('example'),
                'examples': param.get('examples', {})
            }
            normalized.append(normalized_param)
        
        return normalized
    
    def _normalize_request_body(self, request_body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Normalize request body definition."""
        if not request_body:
            return None
        
        return {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'content': request_body.get('content', {})
        }
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Get a list of all endpoints from the specification."""
        endpoints = []
        
        if not self.spec:
            return endpoints
        
        for path, methods in self.spec.get('paths', {}).items():
            for method, operation in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation': operation,
                        'full_url': f"{self.base_url}{path}"
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def get_schemas(self) -> Dict[str, Any]:
        """Get schema definitions from the specification."""
        # OpenAPI 3.0+
        if 'components' in self.spec and 'schemas' in self.spec['components']:
            return self.spec['components']['schemas']
        
        # Swagger 2.0
        if 'definitions' in self.spec:
            return self.spec['definitions']
        
        return {}
    
    def _parse_security_schemes(self) -> Dict[str, Any]:
        """Parse security schemes from the OpenAPI specification."""
        security_schemes = {}
        
        # OpenAPI 3.0+ format
        if 'components' in self.spec and 'securitySchemes' in self.spec['components']:
            schemes = self.spec['components']['securitySchemes']
            for scheme_name, scheme_config in schemes.items():
                security_schemes[scheme_name] = self._normalize_security_scheme(scheme_config)
        
        # Swagger 2.0 format
        elif 'securityDefinitions' in self.spec:
            schemes = self.spec['securityDefinitions']
            for scheme_name, scheme_config in schemes.items():
                security_schemes[scheme_name] = self._normalize_security_scheme(scheme_config)
        
        return security_schemes
    
    def _normalize_security_scheme(self, scheme: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a security scheme configuration."""
        scheme_type = scheme.get('type', '').lower()
        
        normalized = {
            'type': scheme_type,
            'description': scheme.get('description', '')
        }
        
        if scheme_type == 'apikey':
            normalized.update({
                'name': scheme.get('name', 'X-API-Key'),
                'in': scheme.get('in', 'header'),  # 'header', 'query', or 'cookie'
            })
        elif scheme_type == 'http':
            normalized.update({
                'scheme': scheme.get('scheme', 'bearer'),  # 'basic', 'bearer', etc.
                'bearer_format': scheme.get('bearerFormat', 'JWT')
            })
        elif scheme_type == 'oauth2':
            normalized.update({
                'flows': scheme.get('flows', {}),
                'scopes': scheme.get('scopes', {})
            })
        elif scheme_type == 'openidconnect':
            normalized.update({
                'openid_connect_url': scheme.get('openIdConnectUrl', '')
            })
        
        return normalized
    
    def resolve_reference(self, ref: str) -> Dict[str, Any]:
        """Resolve a JSON reference ($ref) in the specification."""
        if not ref.startswith('#/'):
            raise ValueError(f"Only local references are supported: {ref}")
        
        path_parts = ref[2:].split('/')
        current = self.spec
        
        for part in path_parts:
            if part in current:
                current = current[part]
            else:
                raise ValueError(f"Reference not found: {ref}")
        
        return current
