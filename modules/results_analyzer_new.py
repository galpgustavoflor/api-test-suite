"""
Results analyzer for API testing suite.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statistics
from typing import Dict, List, Any, Optional

class ResultsAnalyzer:
    """Analyze and visualize API test results."""
    
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
            'raw_data': self.results,
            'csv_data': self._generate_csv(),
            'performance_chart': self._create_performance_chart()
        }
        
        return self.analysis
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('success', False))
        failed_tests = total_tests - passed_tests
        
        # Calculate response time statistics
        response_times = [
            r.get('response_time', 0) 
            for r in self.results 
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
    
    def _analyze_performance_scenarios(self) -> Dict[str, Any]:
        """Analyze performance test scenarios with enhanced metrics."""
        performance_tests = [r for r in self.results if r.get('test_type') == 'performance']
        
        if not performance_tests:
            return {}
        
        scenarios = {}
        
        # Group by scenario
        for result in performance_tests:
            perf_metrics = result.get('performance_metrics', {})
            scenario_name = perf_metrics.get('scenario', 'default')
            
            if scenario_name not in scenarios:
                scenarios[scenario_name] = {
                    'tests': [],
                    'response_times': [],
                    'functional_success': 0,
                    'performance_success': 0,
                    'total_tests': 0,
                    'scenario_config': perf_metrics
                }
            
            scenarios[scenario_name]['tests'].append(result)
            scenarios[scenario_name]['total_tests'] += 1
            
            if result.get('response_time') is not None:
                scenarios[scenario_name]['response_times'].append(result['response_time'])
            
            if result.get('functional_success', False):
                scenarios[scenario_name]['functional_success'] += 1
            
            if result.get('performance_success', False):
                scenarios[scenario_name]['performance_success'] += 1
        
        # Calculate scenario statistics
        scenario_summary = {}
        for scenario_name, data in scenarios.items():
            response_times = data['response_times']
            total_tests = data['total_tests']
            
            # Calculate response time statistics
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                median_response_time = statistics.median(response_times)
                
                # Calculate percentiles if enough data
                if len(response_times) >= 4:
                    percentile_95 = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                    percentile_99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
                else:
                    percentile_95 = max(response_times)
                    percentile_99 = max(response_times)
            else:
                avg_response_time = 0
                min_response_time = 0
                max_response_time = 0
                median_response_time = 0
                percentile_95 = 0
                percentile_99 = 0
            
            # Calculate success rates
            functional_success_rate = (data['functional_success'] / total_tests * 100) if total_tests > 0 else 0
            performance_success_rate = (data['performance_success'] / total_tests * 100) if total_tests > 0 else 0
            overall_success_rate = min(functional_success_rate, performance_success_rate)
            
            # Get scenario configuration
            config = data['scenario_config']
            expected_max_response_time = config.get('expected_max_response_time', 5000)
            expected_success_rate = config.get('expected_success_rate', 95)
            concurrent = config.get('concurrent', True)
            
            # Determine if scenario passed overall
            scenario_passed = (
                performance_success_rate >= expected_success_rate and
                avg_response_time <= expected_max_response_time
            )
            
            scenario_summary[scenario_name] = {
                'total_tests': total_tests,
                'functional_success': data['functional_success'],
                'performance_success': data['performance_success'],
                'functional_success_rate': round(functional_success_rate, 2),
                'performance_success_rate': round(performance_success_rate, 2),
                'overall_success_rate': round(overall_success_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'min_response_time': round(min_response_time, 2),
                'max_response_time': round(max_response_time, 2),
                'median_response_time': round(median_response_time, 2),
                'percentile_95': round(percentile_95, 2),
                'percentile_99': round(percentile_99, 2),
                'expected_max_response_time': expected_max_response_time,
                'expected_success_rate': expected_success_rate,
                'execution_mode': 'Concurrent' if concurrent else 'Sequential',
                'scenario_passed': scenario_passed,
                'tests': data['tests']
            }
        
        return scenario_summary
    
    def _analyze_status_codes(self) -> Dict[int, int]:
        """Analyze HTTP status code distribution."""
        status_codes = {}
        for result in self.results:
            status_code = result.get('status_code')
            if status_code is not None:
                status_codes[status_code] = status_codes.get(status_code, 0) + 1
        return status_codes
    
    def _analyze_test_types(self) -> Dict[str, Dict[str, Any]]:
        """Analyze results by test type."""
        test_types = {}
        
        for result in self.results:
            test_type = result.get('test_type', 'unknown')
            if test_type not in test_types:
                test_types[test_type] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'avg_response_time': 0.0
                }
            
            test_types[test_type]['total'] += 1
            if result.get('success', False):
                test_types[test_type]['passed'] += 1
            else:
                test_types[test_type]['failed'] += 1
        
        # Calculate averages and success rates
        for test_type, data in test_types.items():
            if data['total'] > 0:
                data['success_rate'] = round((data['passed'] / data['total']) * 100, 2)
            else:
                data['success_rate'] = 0.0
        
        return test_types
    
    def _analyze_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Analyze results by endpoint."""
        endpoints = {}
        
        for result in self.results:
            endpoint_key = f"{result.get('method', 'GET')} {result.get('url', '')}"
            if endpoint_key not in endpoints:
                endpoints[endpoint_key] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'response_times': []
                }
            
            endpoints[endpoint_key]['total'] += 1
            if result.get('success', False):
                endpoints[endpoint_key]['passed'] += 1
            else:
                endpoints[endpoint_key]['failed'] += 1
            
            if result.get('response_time') is not None:
                endpoints[endpoint_key]['response_times'].append(result['response_time'])
        
        # Calculate statistics for each endpoint
        for endpoint, data in endpoints.items():
            if data['total'] > 0:
                data['success_rate'] = round((data['passed'] / data['total']) * 100, 2)
            else:
                data['success_rate'] = 0.0
            
            if data['response_times']:
                data['avg_response_time'] = round(statistics.mean(data['response_times']), 2)
                data['min_response_time'] = round(min(data['response_times']), 2)
                data['max_response_time'] = round(max(data['response_times']), 2)
            else:
                data['avg_response_time'] = 0.0
                data['min_response_time'] = 0.0
                data['max_response_time'] = 0.0
        
        return endpoints
    
    def _analyze_errors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze error patterns."""
        errors = {}
        
        for result in self.results:
            if not result.get('success', False):
                error_type = 'Unknown Error'
                if result.get('error'):
                    error_type = str(result['error'])[:100]  # Limit error message length
                elif result.get('status_code'):
                    error_type = f"HTTP {result['status_code']}"
                
                if error_type not in errors:
                    errors[error_type] = []
                
                errors[error_type].append({
                    'test_name': result.get('test_name', 'Unknown'),
                    'method': result.get('method', 'GET'),
                    'url': result.get('url', ''),
                    'status_code': result.get('status_code'),
                    'error': result.get('error', ''),
                    'response_time': result.get('response_time')
                })
        
        return errors
    
    def _get_passed_tests(self) -> List[Dict[str, Any]]:
        """Get all passed tests."""
        return [r for r in self.results if r.get('success', False)]
    
    def _get_failed_tests(self) -> List[Dict[str, Any]]:
        """Get all failed tests."""
        return [r for r in self.results if not r.get('success', False)]
    
    def _generate_csv(self) -> str:
        """Generate CSV data for download."""
        if not self.results:
            return ""
        
        # Create DataFrame
        df = pd.DataFrame(self.results)
        
        # Select relevant columns
        columns_to_include = [
            'test_name', 'method', 'url', 'status_code', 'response_time',
            'success', 'test_type', 'timestamp', 'error'
        ]
        
        # Only include columns that exist in the data
        available_columns = [col for col in columns_to_include if col in df.columns]
        df_filtered = df[available_columns]
        
        return df_filtered.to_csv(index=False)
    
    def _create_performance_chart(self) -> Optional[go.Figure]:
        """Create performance visualization chart."""
        if not self.results:
            return None
        
        # Prepare data for plotting
        response_times = []
        test_names = []
        status_codes = []
        success_status = []
        test_types = []
        scenarios = []
        
        for i, result in enumerate(self.results):
            if result.get('response_time') is not None:
                response_times.append(result['response_time'])
                test_names.append(f"Test {i+1}")
                status_codes.append(str(result.get('status_code', 'Unknown')))
                success_status.append('Success' if result.get('success', False) else 'Failed')
                test_types.append(result.get('test_type', 'unknown'))
                
                # Get scenario for performance tests
                if result.get('test_type') == 'performance':
                    scenario = result.get('performance_metrics', {}).get('scenario', 'default')
                    scenarios.append(scenario)
                else:
                    scenarios.append('N/A')
        
        if not response_times:
            return None
        
        # Create scatter plot with multiple dimensions
        fig = go.Figure()
        
        # Add scatter plot for response times
        fig.add_trace(go.Scatter(
            x=list(range(len(response_times))),
            y=response_times,
            mode='markers+lines',
            name='Response Time',
            text=[f"Test: {name}<br>Status: {status}<br>Type: {ttype}<br>Scenario: {scenario}" 
                  for name, status, ttype, scenario in zip(test_names, status_codes, test_types, scenarios)],
            hovertemplate='<b>%{text}</b><br>Response Time: %{y}ms<extra></extra>',
            marker=dict(
                size=8,
                color=response_times,
                colorscale='RdYlBu_r',
                colorbar=dict(title="Response Time (ms)"),
                line=dict(width=1, color='DarkSlateGrey')
            )
        ))
        
        fig.update_layout(
            title='API Test Performance Overview',
            xaxis_title='Test Sequence',
            yaxis_title='Response Time (ms)',
            hovermode='closest',
            showlegend=True,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def create_performance_scenario_chart(self) -> Optional[go.Figure]:
        """Create performance scenario comparison chart."""
        performance_summary = self.analysis.get('performance_summary', {})
        
        if not performance_summary:
            return None
        
        scenarios = list(performance_summary.keys())
        avg_response_times = [data['avg_response_time'] for data in performance_summary.values()]
        success_rates = [data['performance_success_rate'] for data in performance_summary.values()]
        expected_times = [data['expected_max_response_time'] for data in performance_summary.values()]
        
        fig = go.Figure()
        
        # Add bar chart for response times
        fig.add_trace(go.Bar(
            x=scenarios,
            y=avg_response_times,
            name='Avg Response Time',
            yaxis='y',
            marker_color='lightblue',
            text=[f"{time}ms" for time in avg_response_times],
            textposition='auto'
        ))
        
        # Add line for expected max response time
        fig.add_trace(go.Scatter(
            x=scenarios,
            y=expected_times,
            name='Expected Max Time',
            yaxis='y',
            mode='lines+markers',
            line=dict(color='red', dash='dash'),
            marker=dict(size=8)
        ))
        
        # Add success rate on secondary y-axis
        fig.add_trace(go.Scatter(
            x=scenarios,
            y=success_rates,
            name='Success Rate (%)',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='green'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Performance Scenarios Comparison',
            xaxis_title='Scenarios',
            yaxis=dict(title='Response Time (ms)', side='left'),
            yaxis2=dict(title='Success Rate (%)', side='right', overlaying='y'),
            hovermode='x unified',
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
