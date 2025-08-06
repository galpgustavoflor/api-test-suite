"""
Results analyzer for API testing suite.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statistics
from typing import Dict, List, Any

class ResultsAnalyzer:
    
from typing import Dict, Any, List, Optional
import json
from collections import Counter, defaultdict
import statistics
import io


class ResultsAnalyzer:
    """Analyzes test results and generates comprehensive reports."""
    
    def __init__(self):
        self.results = []
        self.analysis = {}
    
    def analyze(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze test results and generate comprehensive analysis.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            Analysis dictionary with summary, charts, and detailed data
        """
        self.results = results
        
        if not results:
            return {
                'summary': {
                    'total_tests': 0,
                    'passed': 0,
                    'failed': 0,
                    'error_rate': 0.0,
                    'avg_response_time': 0.0
                },
                'passed_tests': [],
                'failed_tests': [],
                'raw_data': [],
                'csv_data': '',
                'performance_chart': None,
                'status_codes': {},
                'performance_data': []
            }
        
        # Generate analysis
        self.analysis = {
            'summary': self._generate_summary(),
            'performance_data': self._analyze_performance(),
            'performance_summary': self._analyze_performance_scenarios(),
            'status_codes': self._analyze_status_codes(),
            'test_types': self._analyze_test_types(),
            'endpoint_analysis': self._analyze_endpoints(),
            'error_analysis': self._analyze_errors(),
            'passed_tests': self._get_passed_tests(),
            'failed_tests': self._get_failed_tests(),
            'raw_data': results,
            'csv_data': self._generate_csv_data(),
            'performance_chart': self._create_performance_chart()
        }
        
        return self.analysis
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('success', False))
        failed_tests = total_tests - passed_tests
        
        # Calculate response times (excluding None values)
        response_times = [
            r.get('response_time', 0) for r in self.results 
            if r.get('response_time') is not None
        ]
        
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        median_response_time = statistics.median(response_times) if response_times else 0.0
        min_response_time = min(response_times) if response_times else 0.0
        max_response_time = max(response_times) if response_times else 0.0
        
        # Calculate percentiles
        percentile_95 = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0.0
        percentile_99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0.0
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0.0,
            'error_rate': (failed_tests / total_tests * 100) if total_tests > 0 else 0.0,
            'avg_response_time': round(avg_response_time, 2),
            'median_response_time': round(median_response_time, 2),
            'min_response_time': round(min_response_time, 2),
            'max_response_time': round(max_response_time, 2),
            'percentile_95': round(percentile_95, 2),
            'percentile_99': round(percentile_99, 2)
        }
    
    def _analyze_performance(self) -> List[Dict[str, Any]]:
        """Analyze performance metrics."""
        performance_data = []
        
        for result in self.results:
            if result.get('response_time') is not None:
                performance_data.append({
                    'test_name': result.get('test_name', 'Unknown'),
                    'method': result.get('method', 'GET'),
                    'url': result.get('url', ''),
                    'response_time': result.get('response_time'),
                    'status_code': result.get('status_code'),
                    'success': result.get('success', False),
                    'test_type': result.get('test_type', 'unknown'),
                    'timestamp': result.get('timestamp')
                })
        
        return performance_data
    
    def _analyze_status_codes(self) -> Dict[str, int]:
        """Analyze HTTP status code distribution."""
        status_codes = Counter()
        
        for result in self.results:
            status_code = result.get('status_code')
            if status_code is not None:
                status_codes[str(status_code)] += 1
        
        return dict(status_codes)
    
    def _analyze_test_types(self) -> Dict[str, Dict[str, Any]]:
        """Analyze results by test type."""
        test_types = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'avg_response_time': 0.0})
        
        for result in self.results:
            test_type = result.get('test_type', 'unknown')
            test_types[test_type]['total'] += 1
            
            if result.get('success', False):
                test_types[test_type]['passed'] += 1
            else:
                test_types[test_type]['failed'] += 1
            
            # Add to response time calculation
            response_time = result.get('response_time', 0)
            if response_time:
                current_avg = test_types[test_type]['avg_response_time']
                total = test_types[test_type]['total']
                test_types[test_type]['avg_response_time'] = (
                    (current_avg * (total - 1) + response_time) / total
                )
        
        # Convert to regular dict and round averages
        result = {}
        for test_type, data in test_types.items():
            result[test_type] = {
                'total': data['total'],
                'passed': data['passed'],
                'failed': data['failed'],
                'success_rate': (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0.0,
                'avg_response_time': round(data['avg_response_time'], 2)
            }
        
        return result
    
    def _analyze_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Analyze results by endpoint."""
        endpoints = defaultdict(lambda: {
            'total': 0, 'passed': 0, 'failed': 0, 'response_times': []
        })
        
        for result in self.results:
            endpoint_key = f"{result.get('method', 'GET')} {result.get('url', '')}"
            endpoints[endpoint_key]['total'] += 1
            
            if result.get('success', False):
                endpoints[endpoint_key]['passed'] += 1
            else:
                endpoints[endpoint_key]['failed'] += 1
            
            if result.get('response_time') is not None:
                endpoints[endpoint_key]['response_times'].append(result['response_time'])
        
        # Calculate statistics for each endpoint
        result = {}
        for endpoint, data in endpoints.items():
            response_times = data['response_times']
            result[endpoint] = {
                'total': data['total'],
                'passed': data['passed'],
                'failed': data['failed'],
                'success_rate': (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0.0,
                'avg_response_time': round(statistics.mean(response_times), 2) if response_times else 0.0,
                'min_response_time': round(min(response_times), 2) if response_times else 0.0,
                'max_response_time': round(max(response_times), 2) if response_times else 0.0
            }
        
        return result
    
    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze error patterns."""
        errors = []
        error_types = Counter()
        
        for result in self.results:
            if not result.get('success', False):
                error_info = {
                    'test_name': result.get('test_name', 'Unknown'),
                    'method': result.get('method', 'GET'),
                    'url': result.get('url', ''),
                    'status_code': result.get('status_code'),
                    'error': result.get('error', 'Unknown error'),
                    'test_type': result.get('test_type', 'unknown'),
                    'response_body': result.get('response_body', '')
                }
                errors.append(error_info)
                
                # Categorize error types
                if result.get('status_code'):
                    if 400 <= result['status_code'] < 500:
                        error_types['Client Error (4xx)'] += 1
                    elif 500 <= result['status_code'] < 600:
                        error_types['Server Error (5xx)'] += 1
                    else:
                        error_types['Other HTTP Error'] += 1
                else:
                    error_types['Connection Error'] += 1
        
        return {
            'error_details': errors,
            'error_types': dict(error_types),
            'total_errors': len(errors)
        }
    
    def _get_passed_tests(self) -> List[Dict[str, Any]]:
        """Get list of passed tests."""
        passed_tests = []
        
        for result in self.results:
            if result.get('success', False):
                passed_tests.append({
                    'Test Name': result.get('test_name', 'Unknown'),
                    'Method': result.get('method', 'GET'),
                    'URL': result.get('url', ''),
                    'Status Code': result.get('status_code'),
                    'Response Time (ms)': result.get('response_time'),
                    'Test Type': result.get('test_type', 'unknown')
                })
        
        return passed_tests
    
    def _get_failed_tests(self) -> List[Dict[str, Any]]:
        """Get list of failed tests."""
        failed_tests = []
        
        for result in self.results:
            if not result.get('success', False):
                failed_tests.append({
                    'Test Name': result.get('test_name', 'Unknown'),
                    'Method': result.get('method', 'GET'),
                    'URL': result.get('url', ''),
                    'Status Code': result.get('status_code'),
                    'Response Time (ms)': result.get('response_time'),
                    'Error': result.get('error', 'Unknown error'),
                    'Test Type': result.get('test_type', 'unknown')
                })
        
        return failed_tests
    
    def _generate_csv_data(self) -> str:
        """Generate CSV data from results."""
        if not self.results:
            return ''
        
        # Create DataFrame
        df_data = []
        for result in self.results:
            df_data.append({
                'Test ID': result.get('test_id', ''),
                'Test Name': result.get('test_name', ''),
                'Method': result.get('method', ''),
                'URL': result.get('url', ''),
                'Status Code': result.get('status_code', ''),
                'Response Time (ms)': result.get('response_time', ''),
                'Success': result.get('success', False),
                'Error': result.get('error', ''),
                'Test Type': result.get('test_type', ''),
                'Tags': ','.join(result.get('tags', [])),
                'Timestamp': result.get('timestamp', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Convert to CSV string
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    
    def _create_performance_chart(self) -> Optional[go.Figure]:
        """Create performance visualization chart."""
        if not self.results:
            return None
        
        # Prepare data for plotting
        response_times = []
        test_names = []
        status_codes = []
        success_status = []
        
        for i, result in enumerate(self.results):
            if result.get('response_time') is not None:
                response_times.append(result['response_time'])
                test_names.append(f"Test {i+1}")
                status_codes.append(str(result.get('status_code', 'Unknown')))
                success_status.append('Success' if result.get('success', False) else 'Failed')
        
        if not response_times:
            return None
        
        # Create scatter plot
        fig = px.scatter(
            x=range(len(response_times)),
            y=response_times,
            color=success_status,
            hover_data={'Status Code': status_codes},
            title='Response Time Distribution',
            labels={'x': 'Test Number', 'y': 'Response Time (ms)'},
            color_discrete_map={'Success': 'green', 'Failed': 'red'}
        )
        
        # Add average line
        avg_response_time = statistics.mean(response_times)
        fig.add_hline(
            y=avg_response_time,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Average: {avg_response_time:.2f} ms"
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Test Number",
            yaxis_title="Response Time (ms)",
            hovermode='x unified'
        )
        
        return fig
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        if not self.analysis:
            return {}
        
        # Create summary report
        summary = self.analysis['summary']
        
        report = {
            'executive_summary': {
                'total_tests_executed': summary['total_tests'],
                'success_rate': f"{summary['success_rate']:.1f}%",
                'average_response_time': f"{summary['avg_response_time']} ms",
                'tests_passed': summary['passed'],
                'tests_failed': summary['failed']
            },
            'performance_summary': {
                'fastest_response': f"{summary['min_response_time']} ms",
                'slowest_response': f"{summary['max_response_time']} ms",
                'median_response_time': f"{summary['median_response_time']} ms",
                '95th_percentile': f"{summary['percentile_95']} ms",
                '99th_percentile': f"{summary['percentile_99']} ms"
            },
            'test_type_breakdown': self.analysis.get('test_types', {}),
            'endpoint_performance': self.analysis.get('endpoint_analysis', {}),
            'error_analysis': self.analysis.get('error_analysis', {}),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if not self.analysis:
            return recommendations
        
        summary = self.analysis['summary']
        
        # Success rate recommendations
        if summary['success_rate'] < 95:
            recommendations.append(
                f"Success rate is {summary['success_rate']:.1f}%. Consider investigating failed tests."
            )
        
        # Performance recommendations
        if summary['avg_response_time'] > 1000:
            recommendations.append(
                f"Average response time is {summary['avg_response_time']} ms. Consider performance optimization."
            )
        
        # Error analysis recommendations
        error_analysis = self.analysis.get('error_analysis', {})
        if error_analysis.get('total_errors', 0) > 0:
            error_types = error_analysis.get('error_types', {})
            if error_types.get('Server Error (5xx)', 0) > 0:
                recommendations.append("Server errors (5xx) detected. Check server stability and error handling.")
            if error_types.get('Client Error (4xx)', 0) > 0:
                recommendations.append("Client errors (4xx) detected. Review request validation and error responses.")
        
        # Test coverage recommendations
        test_types = self.analysis.get('test_types', {})
        if len(test_types) < 3:
            recommendations.append("Consider adding more test types (edge cases, security tests) for better coverage.")
        
        return recommendations
