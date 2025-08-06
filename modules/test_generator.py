"""
Test case generator for API testing suite.
"""

import random
from typing import Dict, Any, List, Optional, Union
from faker import Faker
import uuid


class TestGenerator:
    """Generates comprehensive test cases from OpenAPI specifications."""
    
    def __init__(self):
        self.fake = Faker()
        self.test_cases = []
        self.security_schemes = {}
    
    def generate_tests(self, spec: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test cases based on OpenAPI specification and configuration.
        
        Args:
            spec: Parsed OpenAPI specification
            config: Test generation configuration
            
        Returns:
            List of generated test cases
        """
        self.test_cases = []
        self.security_schemes = spec.get('security_schemes', {})
        
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                endpoint_tests = self._generate_endpoint_tests(
                    spec['base_url'], path, method, operation, config
                )
                self.test_cases.extend(endpoint_tests)
        
        return self.test_cases
    
    def _generate_endpoint_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate test cases for a specific endpoint."""
        tests = []
        
        # Generate valid data tests
        if config.get('test_valid_data', True):
            valid_tests = self._generate_valid_tests(
                base_url, path, method, operation, config['num_requests']
            )
            tests.extend(valid_tests)
        
        # Generate invalid data tests
        if config.get('test_invalid_data', True):
            invalid_tests = self._generate_invalid_tests(
                base_url, path, method, operation
            )
            tests.extend(invalid_tests)
        
        # Generate edge case tests
        if config.get('test_edge_cases', True):
            edge_tests = self._generate_edge_case_tests(
                base_url, path, method, operation
            )
            tests.extend(edge_tests)
        
        # Generate security tests
        if config.get('test_security', False):
            security_tests = self._generate_security_tests(
                base_url, path, method, operation
            )
            tests.extend(security_tests)
        
        # Generate performance tests
        if config.get('test_performance', False):
            performance_tests = self._generate_performance_tests(
                base_url, path, method, operation, config['num_requests']
            )
            tests.extend(performance_tests)
        
        return tests
    
    def _generate_valid_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any], 
        num_requests: int
    ) -> List[Dict[str, Any]]:
        """Generate tests with valid data."""
        tests = []
        
        for i in range(num_requests):
            test_case = {
                'id': str(uuid.uuid4()),
                'name': f"{method.upper()} {path} - Valid Test {i+1}",
                'method': method.upper(),
                'url': self._build_url(base_url, path, operation.get('parameters', [])),
                'headers': self._generate_headers(operation),
                'body': self._generate_request_body(operation.get('requestBody')),
                'expected_status': self._get_expected_success_status(method, operation),
                'test_type': 'valid',
                'tags': operation.get('tags', []),
                'timeout': 30
            }
            tests.append(test_case)
        
        return tests
    
    def _generate_invalid_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate tests with invalid data."""
        tests = []
        
        # Invalid parameter tests
        for param in operation.get('parameters', []):
            if param.get('required', False):
                test_case = {
                    'id': str(uuid.uuid4()),
                    'name': f"{method.upper()} {path} - Invalid {param['name']}",
                    'method': method.upper(),
                    'url': self._build_url_with_invalid_param(base_url, path, param),
                    'headers': self._generate_headers(operation),
                    'body': self._generate_request_body(operation.get('requestBody')),
                    'expected_status': [400, 422],
                    'test_type': 'invalid',
                    'tags': operation.get('tags', []) + ['validation'],
                    'timeout': 30
                }
                tests.append(test_case)
        
        # Invalid request body tests
        if operation.get('requestBody'):
            invalid_body_test = {
                'id': str(uuid.uuid4()),
                'name': f"{method.upper()} {path} - Invalid Request Body",
                'method': method.upper(),
                'url': self._build_url(base_url, path, operation.get('parameters', [])),
                'headers': self._generate_headers(operation),
                'body': self._generate_invalid_request_body(operation['requestBody']),
                'expected_status': [400, 422],
                'test_type': 'invalid',
                'tags': operation.get('tags', []) + ['validation'],
                'timeout': 30
            }
            tests.append(invalid_body_test)
        
        return tests
    
    def _generate_edge_case_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate edge case tests."""
        tests = []
        
        edge_cases = [
            {
                'name': 'Empty Request Body',
                'body': {},
                'expected_status': [400, 422] if self._is_request_body_required(operation) else [200, 201, 204]
            },
            {
                'name': 'Large Request Body',
                'body': {'data': 'x' * 10000},
                'expected_status': [413, 400]
            },
            {
                'name': 'Special Characters',
                'body': {'test': "!@#$%^&*()[]{}|\\:;\"'<>?/"},
                'expected_status': [200, 201, 400]
            }
        ]
        
        for case in edge_cases:
            test_case = {
                'id': str(uuid.uuid4()),
                'name': f"{method.upper()} {path} - {case['name']}",
                'method': method.upper(),
                'url': self._build_url(base_url, path, operation.get('parameters', [])),
                'headers': self._generate_headers(operation),
                'body': case['body'],
                'expected_status': case['expected_status'],
                'test_type': 'edge_case',
                'tags': operation.get('tags', []) + ['edge_case'],
                'timeout': 30
            }
            tests.append(test_case)
        
        return tests
    
    def _generate_security_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security-focused tests."""
        tests = []
        
        # Get security schemes for this operation
        operation_security = operation.get('security', [])
        
        # Base security tests
        security_tests = [
            {
                'name': 'No Authentication',
                'headers': {'Content-Type': 'application/json'},
                'expected_status': [401, 403]
            }
        ]
        
        # Add scheme-specific security tests
        if hasattr(self, 'security_schemes') and self.security_schemes:
            for scheme_name, scheme_config in self.security_schemes.items():
                scheme_type = scheme_config.get('type', '').lower()
                
                if scheme_type == 'apikey':
                    header_name = scheme_config.get('name', 'X-API-Key')
                    if scheme_config.get('in') == 'header':
                        security_tests.append({
                            'name': f'Invalid {scheme_name} API Key',
                            'headers': {
                                'Content-Type': 'application/json',
                                header_name: 'invalid_api_key_12345'
                            },
                            'expected_status': [401, 403]
                        })
                    elif scheme_config.get('in') == 'query':
                        # This would need URL modification, handled in URL building
                        pass
                
                elif scheme_type == 'http' and scheme_config.get('scheme') == 'bearer':
                    security_tests.append({
                        'name': f'Invalid {scheme_name} Bearer Token',
                        'headers': {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer invalid_token_12345'
                        },
                        'expected_status': [401, 403]
                    })
                
                elif scheme_type == 'http' and scheme_config.get('scheme') == 'basic':
                    security_tests.append({
                        'name': f'Invalid {scheme_name} Basic Auth',
                        'headers': {
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic aW52YWxpZDppbnZhbGlk'  # invalid:invalid in base64
                        },
                        'expected_status': [401, 403]
                    })
        
        # Add generic security tests
        security_tests.extend([
            {
                'name': 'SQL Injection Attempt',
                'body': {'test': "'; DROP TABLE users; --"},
                'expected_status': [400, 422]
            },
            {
                'name': 'XSS Attempt',
                'body': {'test': "<script>alert('xss')</script>"},
                'expected_status': [400, 422]
            }
        ])
        
        for security_test in security_tests:
            test_case = {
                'id': str(uuid.uuid4()),
                'name': f"{method.upper()} {path} - {security_test['name']}",
                'method': method.upper(),
                'url': self._build_url(base_url, path, operation.get('parameters', [])),
                'headers': security_test.get('headers', {'Content-Type': 'application/json'}),
                'body': security_test.get('body', self._generate_request_body(operation.get('requestBody'))),
                'expected_status': security_test['expected_status'],
                'test_type': 'security',
                'tags': operation.get('tags', []) + ['security'],
                'timeout': 30
            }
            tests.append(test_case)
        
        return tests
    
    def _generate_performance_tests(
        self, 
        base_url: str, 
        path: str, 
        method: str, 
        operation: Dict[str, Any],
        num_requests: int
    ) -> List[Dict[str, Any]]:
        """Generate performance-focused tests."""
        tests = []
        
        # Performance test scenarios
        performance_scenarios = [
            {
                'name': 'Load Test',
                'description': 'Standard load test with multiple requests',
                'request_count': min(num_requests * 2, 50),  # Double the normal requests
                'concurrent': True,
                'expected_max_response_time': 5000,  # 5 seconds
                'expected_success_rate': 95.0
            },
            {
                'name': 'Stress Test',
                'description': 'High load stress test',
                'request_count': min(num_requests * 5, 100),  # 5x the normal requests
                'concurrent': True,
                'expected_max_response_time': 10000,  # 10 seconds
                'expected_success_rate': 80.0
            },
            {
                'name': 'Burst Test',
                'description': 'Sudden spike in requests',
                'request_count': min(num_requests * 3, 75),
                'concurrent': True,
                'expected_max_response_time': 8000,  # 8 seconds
                'expected_success_rate': 85.0
            },
            {
                'name': 'Endurance Test',
                'description': 'Sustained load over time',
                'request_count': min(num_requests, 25),
                'concurrent': False,
                'expected_max_response_time': 3000,  # 3 seconds
                'expected_success_rate': 98.0
            }
        ]
        
        for scenario in performance_scenarios:
            # Generate multiple test cases for each scenario
            for i in range(scenario['request_count']):
                test_case = {
                    'id': str(uuid.uuid4()),
                    'name': f"{method.upper()} {path} - {scenario['name']} {i+1}",
                    'method': method.upper(),
                    'url': self._build_url(base_url, path, operation.get('parameters', [])),
                    'headers': self._generate_headers(operation),
                    'body': self._generate_request_body(operation.get('requestBody')),
                    'expected_status': self._get_expected_success_status(method, operation),
                    'test_type': 'performance',
                    'tags': operation.get('tags', []) + ['performance', scenario['name'].lower().replace(' ', '_')],
                    'timeout': 30,
                    'performance_metrics': {
                        'scenario': scenario['name'],
                        'scenario_description': scenario['description'],
                        'expected_max_response_time': scenario['expected_max_response_time'],
                        'expected_success_rate': scenario['expected_success_rate'],
                        'concurrent': scenario['concurrent'],
                        'request_number': i + 1,
                        'total_requests_in_scenario': scenario['request_count']
                    }
                }
                tests.append(test_case)
        
        return tests
    
    def _build_url(self, base_url: str, path: str, parameters: List[Dict[str, Any]]) -> str:
        """Build URL with path and query parameters."""
        # Replace path parameters
        url = base_url + path
        query_params = []
        
        for param in parameters:
            if param['in'] == 'path':
                placeholder = f"{{{param['name']}}}"
                if placeholder in url:
                    value = self._generate_parameter_value(param)
                    url = url.replace(placeholder, str(value))
            elif param['in'] == 'query':
                value = self._generate_parameter_value(param)
                query_params.append(f"{param['name']}={value}")
        
        if query_params:
            url += '?' + '&'.join(query_params)
        
        return url
    
    def _build_url_with_invalid_param(self, base_url: str, path: str, param: Dict[str, Any]) -> str:
        """Build URL with an invalid parameter value."""
        url = base_url + path
        
        if param['in'] == 'path':
            placeholder = f"{{{param['name']}}}"
            if placeholder in url:
                invalid_value = self._generate_invalid_parameter_value(param)
                url = url.replace(placeholder, str(invalid_value))
        elif param['in'] == 'query':
            invalid_value = self._generate_invalid_parameter_value(param)
            url += f"?{param['name']}={invalid_value}"
        
        return url
    
    def _generate_parameter_value(self, param: Dict[str, Any]) -> Union[str, int, float, bool]:
        """Generate a valid value for a parameter."""
        schema = param.get('schema', {})
        param_type = schema.get('type', 'string')
        
        if param.get('example') is not None:
            return param['example']
        
        if param_type == 'integer':
            minimum = schema.get('minimum', 1)
            maximum = schema.get('maximum', 1000)
            return random.randint(minimum, maximum)
        elif param_type == 'number':
            minimum = schema.get('minimum', 1.0)
            maximum = schema.get('maximum', 1000.0)
            return round(random.uniform(minimum, maximum), 2)
        elif param_type == 'boolean':
            return random.choice([True, False])
        elif param_type == 'array':
            return ['item1', 'item2']
        else:  # string
            if schema.get('format') == 'email':
                return self.fake.email()
            elif schema.get('format') == 'date':
                return self.fake.date()
            elif schema.get('format') == 'date-time':
                return self.fake.iso8601()
            elif schema.get('format') == 'uuid':
                return str(uuid.uuid4())
            else:
                enum_values = schema.get('enum')
                if enum_values:
                    return random.choice(enum_values)
                return self.fake.word()
    
    def _generate_invalid_parameter_value(self, param: Dict[str, Any]) -> Union[str, int, float]:
        """Generate an invalid value for a parameter."""
        schema = param.get('schema', {})
        param_type = schema.get('type', 'string')
        
        if param_type == 'integer':
            return 'not_an_integer'
        elif param_type == 'number':
            return 'not_a_number'
        elif param_type == 'boolean':
            return 'not_a_boolean'
        elif param_type == 'array':
            return 'not_an_array'
        else:  # string
            if schema.get('format') == 'email':
                return 'invalid_email'
            elif schema.get('format') == 'date':
                return 'invalid_date'
            elif schema.get('format') == 'date-time':
                return 'invalid_datetime'
            elif schema.get('format') == 'uuid':
                return 'invalid_uuid'
            else:
                # For strings, return a value that violates constraints
                min_length = schema.get('minLength')
                max_length = schema.get('maxLength')
                
                if min_length and min_length > 0:
                    return ''  # Empty string when minimum length is required
                elif max_length:
                    return 'x' * (max_length + 10)  # Exceed maximum length
                else:
                    return 'invalid_string'  # Use a clearly invalid string instead of None
    
    def _generate_headers(self, operation: Dict[str, Any]) -> Dict[str, str]:
        """Generate appropriate headers for the request."""
        headers = {'Content-Type': 'application/json'}
        
        # Check if operation has specific security requirements
        operation_security = operation.get('security', [])
        
        # If no operation-level security, use global security schemes
        if not operation_security and hasattr(self, 'security_schemes'):
            # Use the first available security scheme as default
            for scheme_name, scheme_config in self.security_schemes.items():
                headers.update(self._get_default_auth_headers(scheme_name, scheme_config))
                break  # Use only the first scheme
        
        # Handle operation-level security
        elif operation_security:
            for security_req in operation_security:
                for scheme_name in security_req.keys():
                    if hasattr(self, 'security_schemes') and scheme_name in self.security_schemes:
                        scheme_config = self.security_schemes[scheme_name]
                        headers.update(self._get_default_auth_headers(scheme_name, scheme_config))
                        break
                break  # Use only the first security requirement
        
        # Fallback for legacy specs without proper security schemes
        elif operation.get('security'):
            headers['Authorization'] = 'Bearer test_token'
        
        return headers
    
    def _get_default_auth_headers(self, scheme_name: str, scheme_config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default authentication headers based on security scheme."""
        headers = {}
        scheme_type = scheme_config.get('type', '').lower()
        
        if scheme_type == 'apikey' and scheme_config.get('in') == 'header':
            # Use placeholder value for API key
            header_name = scheme_config.get('name', 'X-API-Key')
            headers[header_name] = f'<{header_name.upper()}_VALUE>'
        
        elif scheme_type == 'http':
            scheme = scheme_config.get('scheme', 'bearer')
            if scheme == 'bearer':
                headers['Authorization'] = 'Bearer <TOKEN_VALUE>'
            elif scheme == 'basic':
                headers['Authorization'] = 'Basic <BASE64_CREDENTIALS>'
        
        elif scheme_type == 'oauth2':
            headers['Authorization'] = 'Bearer <OAUTH2_ACCESS_TOKEN>'
        
        elif scheme_type == 'openidconnect':
            headers['Authorization'] = 'Bearer <OPENID_TOKEN>'
        
        return headers
    
    def _is_request_body_required(self, operation: Dict[str, Any]) -> bool:
        """Check if the request body is required for the operation."""
        request_body = operation.get('requestBody')
        if not request_body:
            return False
        return request_body.get('required', False)
    
    def _generate_request_body(self, request_body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate request body based on schema."""
        if not request_body or 'content' not in request_body:
            return None
        
        content = request_body['content']
        
        # Handle JSON content
        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            return self._generate_object_from_schema(schema)
        
        return None
    
    def _generate_invalid_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Generate invalid request body based on the schema."""
        # Try to extract schema to generate more targeted invalid data
        if 'content' in request_body and 'application/json' in request_body['content']:
            schema = request_body['content']['application/json'].get('schema', {})
            if 'properties' in schema:
                # Generate invalid data by using wrong types for known properties
                invalid_body = {}
                for prop_name, prop_schema in schema['properties'].items():
                    prop_type = prop_schema.get('type', 'string')
                    # Generate wrong type for each property
                    if prop_type == 'string':
                        invalid_body[prop_name] = 12345  # Number instead of string
                    elif prop_type == 'integer':
                        invalid_body[prop_name] = 'not_a_number'  # String instead of integer
                    elif prop_type == 'boolean':
                        invalid_body[prop_name] = 'not_a_boolean'  # String instead of boolean
                    else:
                        invalid_body[prop_name] = None
                return invalid_body
        
        # Fallback to generic invalid data
        return {
            'invalid_field': 'invalid_value',
            'missing_required_fields': True
        }
    
    def _generate_object_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object data from JSON schema."""
        if schema.get('type') != 'object':
            return {}
        
        obj = {}
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for prop_name, prop_schema in properties.items():
            if prop_name in required_fields or random.choice([True, False]):
                obj[prop_name] = self._generate_value_from_schema(prop_schema)
        
        return obj
    
    def _generate_value_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate value based on JSON schema."""
        schema_type = schema.get('type', 'string')
        
        if schema_type == 'string':
            format_type = schema.get('format')
            if format_type == 'email':
                return self.fake.email()
            elif format_type == 'date':
                return self.fake.date()
            elif format_type == 'date-time':
                return self.fake.iso8601()
            else:
                return self.fake.text(max_nb_chars=50)
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 1)
            maximum = schema.get('maximum', 1000)
            return random.randint(minimum, maximum)
        
        elif schema_type == 'number':
            minimum = schema.get('minimum', 1.0)
            maximum = schema.get('maximum', 1000.0)
            return round(random.uniform(minimum, maximum), 2)
        
        elif schema_type == 'boolean':
            return random.choice([True, False])
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._generate_value_from_schema(items_schema) for _ in range(random.randint(1, 3))]
        
        elif schema_type == 'object':
            return self._generate_object_from_schema(schema)
        
        return None
    
    def _get_expected_success_status(self, method: str, operation: Dict[str, Any]) -> List[int]:
        """Get expected success status codes for the operation."""
        responses = operation.get('responses', {})
        success_codes = []
        
        for status_code in responses.keys():
            try:
                code = int(status_code)
                if 200 <= code < 300:
                    success_codes.append(code)
            except ValueError:
                continue
        
        if not success_codes:
            # Default expected status codes by method
            if method.upper() == 'POST':
                success_codes = [201, 200]
            elif method.upper() == 'DELETE':
                success_codes = [204, 200]
            else:
                success_codes = [200]
        
        return success_codes
