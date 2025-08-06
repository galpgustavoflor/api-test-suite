"""
Unit tests for the API Testing Suite modules.
"""

import pytest
import json
import yaml
from pathlib import Path
from modules.swagger_parser import SwaggerParser
from modules.test_generator import TestGenerator
from modules.request_executor import RequestExecutor
from modules.results_analyzer import ResultsAnalyzer


class TestSwaggerParser:
    """Test cases for SwaggerParser."""
    
    def test_parse_valid_swagger(self):
        """Test parsing a valid swagger specification."""
        parser = SwaggerParser()
        
        # Sample minimal OpenAPI spec
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        
        result = parser.parse(spec)
        
        assert result is not None
        assert "paths" in result
        assert "/test" in result["paths"]
        assert "get" in result["paths"]["/test"]
    
    def test_parse_invalid_swagger(self):
        """Test parsing an invalid swagger specification."""
        parser = SwaggerParser()
        
        # Invalid spec (missing required fields)
        spec = {
            "info": {"title": "Test API"}
        }
        
        with pytest.raises(ValueError):
            parser.parse(spec)
    
    def test_get_endpoints(self):
        """Test getting endpoints from parsed specification."""
        parser = SwaggerParser()
        
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/users": {
                    "get": {"summary": "Get users"},
                    "post": {"summary": "Create user"}
                }
            }
        }
        
        parsed_spec = parser.parse(spec)
        endpoints = parser.get_endpoints()
        
        assert len(endpoints) == 2
        assert any(e["method"] == "GET" and e["path"] == "/users" for e in endpoints)
        assert any(e["method"] == "POST" and e["path"] == "/users" for e in endpoints)


class TestTestGenerator:
    """Test cases for TestGenerator."""
    
    def test_generate_tests(self):
        """Test generating test cases from specification."""
        generator = TestGenerator()
        
        spec = {
            "base_url": "https://api.example.com",
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "parameters": [],
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        
        config = {
            "num_requests": 2,
            "test_valid_data": True,
            "test_invalid_data": False,
            "test_edge_cases": False,
            "test_security": False
        }
        
        test_cases = generator.generate_tests(spec, config)
        
        assert len(test_cases) == 2
        assert all("id" in test for test in test_cases)
        assert all("method" in test for test in test_cases)
        assert all("url" in test for test in test_cases)
    
    def test_generate_parameter_value(self):
        """Test parameter value generation."""
        generator = TestGenerator()
        
        # String parameter
        string_param = {
            "name": "test",
            "schema": {"type": "string"}
        }
        value = generator._generate_parameter_value(string_param)
        assert isinstance(value, str)
        
        # Integer parameter
        int_param = {
            "name": "count",
            "schema": {"type": "integer", "minimum": 1, "maximum": 10}
        }
        value = generator._generate_parameter_value(int_param)
        assert isinstance(value, int)
        assert 1 <= value <= 10


class TestRequestExecutor:
    """Test cases for RequestExecutor."""
    
    def test_executor_initialization(self):
        """Test request executor initialization."""
        executor = RequestExecutor(concurrent_requests=10, timeout=60)
        
        assert executor.concurrent_requests == 10
        assert executor.timeout == 60
        assert executor.results == []
    
    def test_execute_single_test_structure(self):
        """Test the structure of a single test result."""
        executor = RequestExecutor()
        
        test_case = {
            "id": "test-1",
            "name": "Test Case 1",
            "method": "GET",
            "url": "https://httpbin.org/get",
            "headers": {"Content-Type": "application/json"},
            "expected_status": [200]
        }
        
        # This will make an actual HTTP request to httpbin.org
        # In a real test environment, you might want to mock this
        result = executor._execute_single_test(test_case)
        
        # Check result structure
        assert "test_id" in result
        assert "test_name" in result
        assert "method" in result
        assert "url" in result
        assert "success" in result
        assert "response_time" in result


class TestResultsAnalyzer:
    """Test cases for ResultsAnalyzer."""
    
    def test_analyze_empty_results(self):
        """Test analyzing empty results."""
        analyzer = ResultsAnalyzer()
        analysis = analyzer.analyze([])
        
        assert analysis["summary"]["total_tests"] == 0
        assert analysis["summary"]["passed"] == 0
        assert analysis["summary"]["failed"] == 0
        assert len(analysis["passed_tests"]) == 0
        assert len(analysis["failed_tests"]) == 0
    
    def test_analyze_results(self):
        """Test analyzing sample results."""
        analyzer = ResultsAnalyzer()
        
        sample_results = [
            {
                "test_id": "1",
                "test_name": "Test 1",
                "method": "GET",
                "url": "https://api.example.com/test",
                "status_code": 200,
                "response_time": 150.5,
                "success": True,
                "error": None,
                "test_type": "valid"
            },
            {
                "test_id": "2",
                "test_name": "Test 2",
                "method": "POST",
                "url": "https://api.example.com/test",
                "status_code": 400,
                "response_time": 200.0,
                "success": False,
                "error": "Bad Request",
                "test_type": "invalid"
            }
        ]
        
        analysis = analyzer.analyze(sample_results)
        
        assert analysis["summary"]["total_tests"] == 2
        assert analysis["summary"]["passed"] == 1
        assert analysis["summary"]["failed"] == 1
        assert analysis["summary"]["success_rate"] == 50.0
        assert analysis["summary"]["avg_response_time"] == 175.25
    
    def test_generate_csv_data(self):
        """Test CSV data generation."""
        analyzer = ResultsAnalyzer()
        
        sample_results = [
            {
                "test_id": "1",
                "test_name": "Test 1",
                "method": "GET",
                "url": "https://api.example.com/test",
                "status_code": 200,
                "response_time": 150.5,
                "success": True,
                "error": None,
                "test_type": "valid",
                "tags": ["api"],
                "timestamp": 1234567890
            }
        ]
        
        analysis = analyzer.analyze(sample_results)
        csv_data = analysis["csv_data"]
        
        assert "Test ID" in csv_data
        assert "Test Name" in csv_data
        assert "Method" in csv_data
        assert "URL" in csv_data


def test_example_files_exist():
    """Test that example files exist and are valid."""
    examples_dir = Path("examples")
    
    # Test YAML file
    yaml_file = examples_dir / "petstore-api.yaml"
    assert yaml_file.exists()
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_content = yaml.safe_load(f)
    assert "openapi" in yaml_content
    assert "paths" in yaml_content
    
    # Test JSON file
    json_file = examples_dir / "user-management-api.json"
    assert json_file.exists()
    
    with open(json_file, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    assert "openapi" in json_content
    assert "paths" in json_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
