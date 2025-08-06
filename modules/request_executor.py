"""
Request executor for API testing suite with concurrent execution support.
"""

import asyncio
import aiohttp
import requests
import time
import warnings
from typing import Dict, Any, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from urllib.parse import urlparse

# Suppress SSL warnings for testing environments
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)


class RequestExecutor:
    """Executes HTTP requests with support for concurrent execution and load testing."""
    
    def __init__(self, concurrent_requests: int = 5, timeout: int = 30, auth_config: Dict[str, Any] = None):
        self.concurrent_requests = concurrent_requests
        self.timeout = timeout
        self.auth_config = auth_config or {}
        self.results = []
        self.session = None
    
    def execute_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute all test cases with concurrent processing.
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            List of test results
        """
        self.results = []
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            # Submit all test cases
            future_to_test = {
                executor.submit(self._execute_single_test, test_case): test_case 
                for test_case in test_cases
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = {
                        'test_id': test_case.get('id', 'unknown'),
                        'test_name': test_case.get('name', 'unknown'),
                        'method': test_case.get('method', 'GET'),
                        'url': test_case.get('url', ''),
                        'status_code': None,
                        'response_time': None,
                        'success': False,
                        'error': str(e),
                        'response_body': None,
                        'response_headers': None,
                        'test_type': test_case.get('test_type', 'unknown'),
                        'timestamp': time.time()
                    }
                    self.results.append(error_result)
        
        return self.results
    
    def execute_performance_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute performance tests with enhanced metrics collection.
        
        Args:
            test_cases: List of performance test case dictionaries
            
        Returns:
            List of test results with performance metrics
        """
        # Separate performance tests by scenario
        scenarios = {}
        for test_case in test_cases:
            if test_case.get('test_type') == 'performance':
                scenario_name = test_case.get('performance_metrics', {}).get('scenario', 'default')
                if scenario_name not in scenarios:
                    scenarios[scenario_name] = []
                scenarios[scenario_name].append(test_case)
        
        all_results = []
        
        # Execute each scenario
        for scenario_name, scenario_tests in scenarios.items():
            print(f"Executing performance scenario: {scenario_name}")
            
            # Check if scenario should run concurrently
            concurrent = scenario_tests[0].get('performance_metrics', {}).get('concurrent', True)
            
            if concurrent:
                # Execute concurrently for load/stress tests
                scenario_results = self._execute_concurrent_performance_tests(scenario_tests)
            else:
                # Execute sequentially for endurance tests
                scenario_results = self._execute_sequential_performance_tests(scenario_tests)
            
            all_results.extend(scenario_results)
        
        # Execute non-performance tests normally
        non_performance_tests = [t for t in test_cases if t.get('test_type') != 'performance']
        if non_performance_tests:
            regular_results = self.execute_tests(non_performance_tests)
            all_results.extend(regular_results)
        
        return all_results
    
    def _execute_concurrent_performance_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute performance tests concurrently."""
        results = []
        start_time = time.time()
        
        # Use higher concurrency for performance tests
        max_workers = min(len(test_cases), self.concurrent_requests * 2)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test cases
            future_to_test = {
                executor.submit(self._execute_performance_test, test_case, start_time): test_case 
                for test_case in test_cases
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    # Create error result for failed tests
                    error_result = {
                        'test_id': test_case.get('id', 'unknown'),
                        'test_name': test_case.get('name', 'unknown'),
                        'method': test_case.get('method', 'GET'),
                        'url': test_case.get('url', ''),
                        'status_code': None,
                        'response_time': None,
                        'success': False,
                        'error': str(exc),
                        'response_body': None,
                        'response_headers': None,
                        'test_type': test_case.get('test_type', 'performance'),
                        'timestamp': time.time(),
                        'performance_metrics': test_case.get('performance_metrics', {})
                    }
                    results.append(error_result)
        
        return results
    
    def _execute_sequential_performance_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute performance tests sequentially for endurance testing."""
        results = []
        scenario_start_time = time.time()
        
        for test_case in test_cases:
            result = self._execute_performance_test(test_case, scenario_start_time)
            results.append(result)
            
            # Small delay between requests for endurance testing
            time.sleep(0.1)
        
        return results
    
    def _execute_performance_test(self, test_case: Dict[str, Any], scenario_start_time: float) -> Dict[str, Any]:
        """Execute a single performance test with enhanced metrics."""
        test_start_time = time.time()
        
        try:
            # Prepare request parameters
            method = test_case.get('method', 'GET').upper()
            url = test_case.get('url', '')
            headers = test_case.get('headers', {}).copy()
            body = test_case.get('body')
            timeout = test_case.get('timeout', self.timeout)
            expected_status = test_case.get('expected_status', [200])
            performance_metrics = test_case.get('performance_metrics', {})
            
            # Apply authentication
            url, headers, body = self._apply_authentication(url, headers, body)
            
            # Ensure expected_status is a list
            if isinstance(expected_status, int):
                expected_status = [expected_status]
            
            # Make the HTTP request
            response = self._make_request(method, url, headers, body, timeout)
            
            end_time = time.time()
            response_time = round((end_time - test_start_time) * 1000, 2)  # in milliseconds
            
            # Determine if test was successful
            success = response.status_code in expected_status
            
            # Check performance criteria
            max_response_time = performance_metrics.get('expected_max_response_time', 5000)
            performance_success = response_time <= max_response_time
            
            # Parse response body
            response_body = None
            try:
                response_body = response.json()
            except:
                response_body = response.text[:1000]  # Limit response body size
            
            # Calculate time since scenario start
            time_since_scenario_start = round((test_start_time - scenario_start_time) * 1000, 2)
            
            # Create result with performance metrics
            result = {
                'test_id': test_case.get('id', 'unknown'),
                'test_name': test_case.get('name', 'unknown'),
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': success and performance_success,
                'performance_success': performance_success,
                'functional_success': success,
                'error': None,
                'response_body': response_body,
                'response_headers': dict(response.headers),
                'test_type': test_case.get('test_type', 'performance'),
                'expected_status': expected_status,
                'tags': test_case.get('tags', []),
                'timestamp': test_start_time,
                'performance_metrics': {
                    **performance_metrics,
                    'actual_response_time': response_time,
                    'time_since_scenario_start': time_since_scenario_start,
                    'performance_passed': performance_success,
                    'functional_passed': success,
                    'max_response_time_threshold': max_response_time
                }
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - test_start_time) * 1000, 2)
            time_since_scenario_start = round((test_start_time - scenario_start_time) * 1000, 2)
            
            result = {
                'test_id': test_case.get('id', 'unknown'),
                'test_name': test_case.get('name', 'unknown'),
                'method': test_case.get('method', 'GET'),
                'url': test_case.get('url', ''),
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'performance_success': False,
                'functional_success': False,
                'error': str(e),
                'response_body': None,
                'response_headers': None,
                'test_type': test_case.get('test_type', 'performance'),
                'expected_status': test_case.get('expected_status', [200]),
                'tags': test_case.get('tags', []),
                'timestamp': test_start_time,
                'performance_metrics': {
                    **test_case.get('performance_metrics', {}),
                    'actual_response_time': response_time,
                    'time_since_scenario_start': time_since_scenario_start,
                    'performance_passed': False,
                    'functional_passed': False,
                    'error': str(e)
                }
            }
            
        return result
    
    def _execute_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case.
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            Test result dictionary
        """
        start_time = time.time()
        
        try:
            # Prepare request parameters
            method = test_case.get('method', 'GET').upper()
            url = test_case.get('url', '')
            headers = test_case.get('headers', {}).copy()  # Copy to avoid modifying original
            body = test_case.get('body')
            timeout = test_case.get('timeout', self.timeout)
            expected_status = test_case.get('expected_status', [200])
            
            # Apply authentication
            url, headers, body = self._apply_authentication(url, headers, body)
            
            # Ensure expected_status is a list
            if isinstance(expected_status, int):
                expected_status = [expected_status]
            
            # Make the HTTP request
            response = self._make_request(method, url, headers, body, timeout)
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # in milliseconds
            
            # Determine if test was successful
            success = response.status_code in expected_status
            
            # Parse response body
            response_body = None
            try:
                response_body = response.json()
            except:
                response_body = response.text[:1000]  # Limit response body size
            
            # Create result
            result = {
                'test_id': test_case.get('id', 'unknown'),
                'test_name': test_case.get('name', 'unknown'),
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': success,
                'error': None,
                'response_body': response_body,
                'response_headers': dict(response.headers),
                'test_type': test_case.get('test_type', 'unknown'),
                'expected_status': expected_status,
                'tags': test_case.get('tags', []),
                'timestamp': start_time
            }
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            # Create error result
            result = {
                'test_id': test_case.get('id', 'unknown'),
                'test_name': test_case.get('name', 'unknown'),
                'method': test_case.get('method', 'GET'),
                'url': test_case.get('url', ''),
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'response_body': None,
                'response_headers': None,
                'test_type': test_case.get('test_type', 'unknown'),
                'expected_status': test_case.get('expected_status', [200]),
                'tags': test_case.get('tags', []),
                'timestamp': start_time
            }
            
            return result
    
    def _apply_authentication(self, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]]) -> tuple:
        """
        Apply authentication configuration to request.
        
        Args:
            url: Request URL
            headers: Request headers
            body: Request body
            
        Returns:
            Tuple of (modified_url, modified_headers, modified_body)
        """
        if not self.auth_config or self.auth_config.get('type') == 'none':
            return url, headers, body
        
        auth_type = self.auth_config.get('type')
        
        if auth_type == 'api_key':
            location = self.auth_config.get('location', 'header')
            name = self.auth_config.get('name', 'X-API-Key')
            value = self.auth_config.get('value', '')
            
            if location == 'header':
                headers[name] = value
            elif location == 'query_parameter':
                # Add to URL query parameters
                separator = '&' if '?' in url else '?'
                url = f"{url}{separator}{name}={value}"
                
        elif auth_type == 'bearer_token':
            token = self.auth_config.get('value', '')
            headers['Authorization'] = f"Bearer {token}"
            
        elif auth_type == 'basic_auth':
            import base64
            username = self.auth_config.get('username', '')
            password = self.auth_config.get('password', '')
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f"Basic {credentials}"
            
        elif auth_type == 'custom_header':
            name = self.auth_config.get('name', '')
            value = self.auth_config.get('value', '')
            if name:
                headers[name] = value
        
        return url, headers, body
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[Dict[str, Any]], 
        timeout: int
    ) -> requests.Response:
        """
        Make HTTP request using requests library.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            timeout: Request timeout
            
        Returns:
            Response object
        """
        # Prepare request arguments
        request_args = {
            'url': url,
            'headers': headers,
            'timeout': timeout,
            'verify': False  # Disable SSL verification for testing
        }
        
        # Add body for appropriate methods
        if method in ['POST', 'PUT', 'PATCH'] and body is not None:
            if isinstance(body, dict):
                request_args['json'] = body
            else:
                request_args['data'] = body
        
        # Make request based on method
        if method == 'GET':
            return requests.get(**request_args)
        elif method == 'POST':
            return requests.post(**request_args)
        elif method == 'PUT':
            return requests.put(**request_args)
        elif method == 'DELETE':
            return requests.delete(**request_args)
        elif method == 'PATCH':
            return requests.patch(**request_args)
        elif method == 'OPTIONS':
            return requests.options(**request_args)
        elif method == 'HEAD':
            return requests.head(**request_args)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    async def execute_tests_async(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tests asynchronously using aiohttp.
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            List of test results
        """
        self.results = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.concurrent_requests)
        
        # Create aiohttp session
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Create tasks for all test cases
            tasks = [
                self._execute_single_test_async(session, semaphore, test_case)
                for test_case in test_cases
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    test_case = test_cases[i]
                    error_result = {
                        'test_id': test_case.get('id', 'unknown'),
                        'test_name': test_case.get('name', 'unknown'),
                        'method': test_case.get('method', 'GET'),
                        'url': test_case.get('url', ''),
                        'status_code': None,
                        'response_time': None,
                        'success': False,
                        'error': str(result),
                        'response_body': None,
                        'response_headers': None,
                        'test_type': test_case.get('test_type', 'unknown'),
                        'timestamp': time.time()
                    }
                    self.results.append(error_result)
                else:
                    self.results.append(result)
        
        return self.results
    
    async def _execute_single_test_async(
        self, 
        session: aiohttp.ClientSession, 
        semaphore: asyncio.Semaphore, 
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single test case asynchronously.
        
        Args:
            session: aiohttp ClientSession
            semaphore: Semaphore for rate limiting
            test_case: Test case dictionary
            
        Returns:
            Test result dictionary
        """
        async with semaphore:
            start_time = time.time()
            
            try:
                # Prepare request parameters
                method = test_case.get('method', 'GET').upper()
                url = test_case.get('url', '')
                headers = test_case.get('headers', {}).copy()  # Copy to avoid modifying original
                body = test_case.get('body')
                expected_status = test_case.get('expected_status', [200])
                
                # Apply authentication
                url, headers, body = self._apply_authentication(url, headers, body)
                
                # Ensure expected_status is a list
                if isinstance(expected_status, int):
                    expected_status = [expected_status]
                
                # Prepare request arguments
                request_args = {
                    'url': url,
                    'headers': headers
                }
                
                # Add body for appropriate methods
                if method in ['POST', 'PUT', 'PATCH'] and body is not None:
                    if isinstance(body, dict):
                        request_args['json'] = body
                    else:
                        request_args['data'] = body
                
                # Make the request
                async with session.request(method, **request_args) as response:
                    end_time = time.time()
                    response_time = round((end_time - start_time) * 1000, 2)
                    
                    # Read response body
                    try:
                        response_body = await response.json()
                    except:
                        response_body = await response.text()
                        response_body = response_body[:1000]  # Limit size
                    
                    # Determine success
                    success = response.status in expected_status
                    
                    # Create result
                    result = {
                        'test_id': test_case.get('id', 'unknown'),
                        'test_name': test_case.get('name', 'unknown'),
                        'method': method,
                        'url': url,
                        'status_code': response.status,
                        'response_time': response_time,
                        'success': success,
                        'error': None,
                        'response_body': response_body,
                        'response_headers': dict(response.headers),
                        'test_type': test_case.get('test_type', 'unknown'),
                        'expected_status': expected_status,
                        'tags': test_case.get('tags', []),
                        'timestamp': start_time
                    }
                    
                    return result
                    
            except Exception as e:
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)
                
                # Create error result
                result = {
                    'test_id': test_case.get('id', 'unknown'),
                    'test_name': test_case.get('name', 'unknown'),
                    'method': test_case.get('method', 'GET'),
                    'url': test_case.get('url', ''),
                    'status_code': None,
                    'response_time': response_time,
                    'success': False,
                    'error': str(e),
                    'response_body': None,
                    'response_headers': None,
                    'test_type': test_case.get('test_type', 'unknown'),
                    'expected_status': test_case.get('expected_status', [200]),
                    'tags': test_case.get('tags', []),
                    'timestamp': start_time
                }
                
                return result
    
    def execute_load_test(
        self, 
        test_case: Dict[str, Any], 
        duration_seconds: int, 
        requests_per_second: int
    ) -> List[Dict[str, Any]]:
        """
        Execute a load test for a specific endpoint.
        
        Args:
            test_case: Test case to run repeatedly
            duration_seconds: Duration of the load test
            requests_per_second: Target requests per second
            
        Returns:
            List of all test results
        """
        load_test_results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        request_interval = 1.0 / requests_per_second
        next_request_time = start_time
        
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            futures = []
            
            while time.time() < end_time:
                current_time = time.time()
                
                if current_time >= next_request_time:
                    # Submit request
                    future = executor.submit(self._execute_single_test, test_case.copy())
                    futures.append(future)
                    
                    # Schedule next request
                    next_request_time += request_interval
                
                # Small sleep to prevent busy waiting
                time.sleep(0.001)
            
            # Collect all results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    load_test_results.append(result)
                except Exception as e:
                    error_result = {
                        'test_id': test_case.get('id', 'load_test'),
                        'test_name': f"Load Test - {test_case.get('name', 'unknown')}",
                        'method': test_case.get('method', 'GET'),
                        'url': test_case.get('url', ''),
                        'status_code': None,
                        'response_time': None,
                        'success': False,
                        'error': str(e),
                        'response_body': None,
                        'response_headers': None,
                        'test_type': 'load_test',
                        'timestamp': time.time()
                    }
                    load_test_results.append(error_result)
        
        return load_test_results
