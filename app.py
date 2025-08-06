import streamlit as st
import yaml
import json
from pathlib import Path
import io
from typing import Dict, Any, List
import pandas as pd

from modules.swagger_parser import SwaggerParser
from modules.test_generator import TestGenerator
from modules.request_executor import RequestExecutor
from modules.results_analyzer import ResultsAnalyzer


def get_auth_suggestion(scheme_config: Dict[str, Any]) -> str:
    """Get authentication configuration suggestion based on detected security scheme."""
    scheme_type = scheme_config.get('type', '').lower()
    
    if scheme_type == 'apikey':
        location = scheme_config.get('in', 'header')
        name = scheme_config.get('name', 'X-API-Key')
        
        if location == 'header':
            return f"Configure 'API Key' authentication with Header name: '{name}'"
        elif location == 'query':
            return f"Configure 'API Key' authentication with Query parameter: '{name}'"
        else:
            return f"Configure 'Custom Header' with name: '{name}'"
    
    elif scheme_type == 'http':
        scheme = scheme_config.get('scheme', 'bearer')
        if scheme == 'bearer':
            return "Configure 'Bearer Token' authentication"
        elif scheme == 'basic':
            return "Configure 'Basic Auth' authentication"
        else:
            return f"Configure 'Custom Header' for HTTP {scheme} authentication"
    
    elif scheme_type == 'oauth2':
        return "OAuth2 flow detected - use 'Bearer Token' with your OAuth2 access token"
    
    elif scheme_type == 'openidconnect':
        return "OpenID Connect detected - use 'Bearer Token' with your ID token"
    
    return "Custom authentication scheme detected"


def main():
    """Main Streamlit application for API testing suite."""
    
    st.set_page_config(
        page_title="API Testing Suite",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧪 API Testing Suite")
    st.markdown("**Massive API testing based on Swagger/OpenAPI specifications**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Authentication configuration
        st.subheader("🔐 Authentication")
        auth_type = st.selectbox(
            "Authentication Type",
            ["None", "API Key", "Bearer Token", "Basic Auth", "Custom Header"]
        )
        
        auth_config = {}
        if auth_type == "API Key":
            api_key_location = st.selectbox("API Key Location", ["Header", "Query Parameter"])
            api_key_name = st.text_input(
                "API Key Name", 
                value="X-API-Key" if api_key_location == "Header" else "api_key",
                help="Name of the header or query parameter for the API key"
            )
            api_key_value = st.text_input("API Key Value", type="password", help="Your API key")
            if api_key_value:
                auth_config = {
                    "type": "api_key",
                    "location": api_key_location.lower().replace(" ", "_"),
                    "name": api_key_name,
                    "value": api_key_value
                }
        elif auth_type == "Bearer Token":
            token_value = st.text_input("Bearer Token", type="password", help="JWT or Bearer token")
            if token_value:
                auth_config = {
                    "type": "bearer_token",
                    "value": token_value
                }
        elif auth_type == "Basic Auth":
            username = st.text_input("Username", help="Basic auth username")
            password = st.text_input("Password", type="password", help="Basic auth password")
            if username and password:
                auth_config = {
                    "type": "basic_auth",
                    "username": username,
                    "password": password
                }
        elif auth_type == "Custom Header":
            header_name = st.text_input("Header Name", help="Custom header name")
            header_value = st.text_input("Header Value", type="password", help="Custom header value")
            if header_name and header_value:
                auth_config = {
                    "type": "custom_header",
                    "name": header_name,
                    "value": header_value
                }
        
        if auth_config:
            st.success(f"✅ {auth_type} authentication configured")
        else:
            st.info("ℹ️ No authentication configured")
        
        st.divider()
        
        # Test configuration
        st.subheader("Test Settings")
        num_requests = st.slider("Number of requests per endpoint", 1, 1000, 10)
        concurrent_requests = st.slider("Concurrent requests", 1, 50, 5)
        timeout = st.number_input("Request timeout (seconds)", 1, 60, 10)
        
        # Test types
        st.subheader("Test Types")
        test_valid_data = st.checkbox("Valid data tests", True)
        test_invalid_data = st.checkbox("Invalid data tests", True)
        test_edge_cases = st.checkbox("Edge case tests", True)
        test_security = st.checkbox("Security tests", False)
        test_performance = st.checkbox("Performance tests", False)
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📄 Swagger Specification")
        
        # Input methods
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Paste YAML/JSON"]
        )
        
        swagger_content = None
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload Swagger/OpenAPI file",
                type=['yaml', 'yml', 'json'],
                help="Upload your OpenAPI/Swagger specification file"
            )
            
            if uploaded_file:
                try:
                    content = uploaded_file.read()
                    if uploaded_file.type == "application/json":
                        swagger_content = json.loads(content)
                    else:
                        swagger_content = yaml.safe_load(content)
                    st.success(f"✅ File uploaded: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ Error parsing file: {str(e)}")
        
        else:
            swagger_text = st.text_area(
                "Paste Swagger/OpenAPI specification:",
                height=300,
                help="Paste your YAML or JSON specification here"
            )
            
            if swagger_text:
                try:
                    # Try JSON first, then YAML
                    try:
                        swagger_content = json.loads(swagger_text)
                    except json.JSONDecodeError:
                        swagger_content = yaml.safe_load(swagger_text)
                    st.success("✅ Specification parsed successfully")
                except Exception as e:
                    st.error(f"❌ Error parsing specification: {str(e)}")
    
    with col2:
        st.header("🔧 Test Generation & Execution")
        
        if swagger_content:
            try:
                # Parse swagger specification
                parser = SwaggerParser()
                parsed_spec = parser.parse(swagger_content)
                
                # Display API information
                st.subheader("API Information")
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.metric("API Title", parsed_spec.get('info', {}).get('title', 'N/A'))
                    st.metric("Version", parsed_spec.get('info', {}).get('version', 'N/A'))
                
                with info_col2:
                    endpoints = len(parsed_spec.get('paths', {}))
                    st.metric("Total Endpoints", endpoints)
                    
                    # Count methods
                    total_methods = sum(
                        len(methods) for methods in parsed_spec.get('paths', {}).values()
                    )
                    st.metric("Total Methods", total_methods)
                
                # Show endpoints summary
                st.subheader("📋 Endpoints Summary")
                endpoints_data = []
                
                for path, methods in parsed_spec.get('paths', {}).items():
                    for method, details in methods.items():
                        if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
                            endpoints_data.append({
                                'Path': path,
                                'Method': method.upper(),
                                'Summary': details.get('summary', 'N/A'),
                                'Parameters': len(details.get('parameters', [])),
                                'Responses': len(details.get('responses', {}))
                            })
                
                if endpoints_data:
                    df = pd.DataFrame(endpoints_data)
                    st.dataframe(df, use_container_width=True)
                
                # Show detected security schemes
                security_schemes = parsed_spec.get('security_schemes', {})
                if security_schemes:
                    st.subheader("🔐 Detected Security Schemes")
                    
                    for scheme_name, scheme_config in security_schemes.items():
                        with st.expander(f"🔑 {scheme_name}", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Type:** {scheme_config.get('type', 'N/A')}")
                                if scheme_config.get('description'):
                                    st.write(f"**Description:** {scheme_config['description']}")
                            
                            with col2:
                                if scheme_config.get('type') == 'apikey':
                                    st.write(f"**Name:** `{scheme_config.get('name', 'N/A')}`")
                                    st.write(f"**Location:** {scheme_config.get('in', 'N/A')}")
                                elif scheme_config.get('type') == 'http':
                                    st.write(f"**Scheme:** {scheme_config.get('scheme', 'N/A')}")
                                    if scheme_config.get('bearer_format'):
                                        st.write(f"**Bearer Format:** {scheme_config['bearer_format']}")
                            
                            # Show authentication suggestion
                            suggestion = get_auth_suggestion(scheme_config)
                            if suggestion:
                                st.info(f"💡 **Suggestion:** {suggestion}")
                
                # Test generation and execution
                if st.button("🚀 Generate and Execute Tests", type="primary", use_container_width=True):
                    with st.spinner("Generating and executing tests..."):
                        # Generate test cases
                        generator = TestGenerator()
                        test_config = {
                            'num_requests': num_requests,
                            'test_valid_data': test_valid_data,
                            'test_invalid_data': test_invalid_data,
                            'test_edge_cases': test_edge_cases,
                            'test_security': test_security,
                            'test_performance': test_performance
                        }
                        
                        test_cases = generator.generate_tests(parsed_spec, test_config)
                        st.success(f"✅ Generated {len(test_cases)} test cases")
                        
                        # Execute tests with authentication
                        executor = RequestExecutor(
                            concurrent_requests=concurrent_requests,
                            timeout=timeout,
                            auth_config=auth_config
                        )
                        
                        # Use performance execution if performance tests are enabled
                        if test_performance:
                            results = executor.execute_performance_tests(test_cases)
                        else:
                            results = executor.execute_tests(test_cases)
                        
                        # Analyze and display results
                        analyzer = ResultsAnalyzer()
                        analysis = analyzer.analyze(results)
                        
                        display_results(analysis)
                        
            except Exception as e:
                st.error(f"❌ Error processing specification: {str(e)}")
                st.exception(e)
        else:
            st.info("👆 Please upload or paste a Swagger/OpenAPI specification to get started")

def display_results(analysis: Dict[str, Any]):
    """Display test results in a comprehensive format."""
    
    st.header("📊 Test Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tests", 
            analysis['summary']['total_tests'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Passed", 
            analysis['summary']['passed'],
            delta=analysis['summary']['passed'] - analysis['summary']['failed'],
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Failed", 
            analysis['summary']['failed'],
            delta=analysis['summary']['failed'],
            delta_color="inverse"
        )
    
    with col4:
        success_rate = (analysis['summary']['passed'] / analysis['summary']['total_tests']) * 100
        st.metric(
            "Success Rate", 
            f"{success_rate:.1f}%",
            delta=f"{success_rate:.1f}%"
        )
    
    # Detailed results tabs
    performance_summary = analysis.get('performance_summary', {})
    if performance_summary:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "🚀 Performance", "✅ Passed Tests", "❌ Failed Tests", "📋 Raw Data"])
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "✅ Passed Tests", "❌ Failed Tests", "📋 Raw Data"])
    
    with tab1:
        # Performance chart
        if analysis.get('performance_data'):
            st.subheader("Response Time Distribution")
            st.plotly_chart(analysis['performance_chart'], use_container_width=True)
        
        # Status code distribution
        if analysis.get('status_codes'):
            st.subheader("HTTP Status Code Distribution")
            st.bar_chart(analysis['status_codes'])
    
    # Performance tab (only shown if performance tests were run)
    if performance_summary:
        with tab2:
            st.subheader("🚀 Performance Test Results")
            
            # Performance scenarios overview
            for scenario_name, scenario_data in performance_summary.items():
                with st.container():
                    st.markdown(f"### {scenario_name.replace('_', ' ').title()}")
                    
                    # Scenario metrics
                    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                    
                    with perf_col1:
                        st.metric(
                            "Tests", 
                            scenario_data['total_tests']
                        )
                    
                    with perf_col2:
                        st.metric(
                            "Avg Response Time",
                            f"{scenario_data['avg_response_time']}ms",
                            delta=f"-{scenario_data['expected_max_response_time'] - scenario_data['avg_response_time']}ms" 
                                  if scenario_data['avg_response_time'] <= scenario_data['expected_max_response_time'] 
                                  else f"+{scenario_data['avg_response_time'] - scenario_data['expected_max_response_time']}ms",
                            delta_color="normal" if scenario_data['avg_response_time'] <= scenario_data['expected_max_response_time'] else "inverse"
                        )
                    
                    with perf_col3:
                        st.metric(
                            "Performance Success Rate",
                            f"{scenario_data['performance_success_rate']}%",
                            delta=f"{scenario_data['performance_success_rate'] - scenario_data['expected_success_rate']}%"
                        )
                    
                    with perf_col4:
                        status = "✅ PASSED" if scenario_data['scenario_passed'] else "❌ FAILED"
                        st.markdown(f"**Scenario Status:** {status}")
                    
                    # Scenario details
                    details_col1, details_col2 = st.columns(2)
                    
                    with details_col1:
                        st.markdown("**Response Time Statistics:**")
                        st.write(f"• Min: {scenario_data['min_response_time']}ms")
                        st.write(f"• Max: {scenario_data['max_response_time']}ms")
                        st.write(f"• Median: {scenario_data['median_response_time']}ms")
                        st.write(f"• 95th Percentile: {scenario_data['percentile_95']}ms")
                        st.write(f"• 99th Percentile: {scenario_data['percentile_99']}ms")
                    
                    with details_col2:
                        st.markdown("**Test Configuration:**")
                        st.write(f"• Expected Max Response Time: {scenario_data['expected_max_response_time']}ms")
                        st.write(f"• Expected Success Rate: {scenario_data['expected_success_rate']}%")
                        st.write(f"• Execution Mode: {scenario_data['execution_mode']}")
                        st.write(f"• Functional Success: {scenario_data['functional_success']}/{scenario_data['total_tests']}")
                        st.write(f"• Performance Success: {scenario_data['performance_success']}/{scenario_data['total_tests']}")
                    
                    st.divider()
            
            # Performance scenario comparison chart
            try:
                from modules.results_analyzer import ResultsAnalyzer
                analyzer = ResultsAnalyzer()
                analyzer.analysis = analysis  # Set the analysis data
                scenario_chart = analyzer.create_performance_scenario_chart()
                if scenario_chart:
                    st.subheader("Performance Scenarios Comparison")
                    st.plotly_chart(scenario_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate performance comparison chart: {str(e)}")
        
        # Remaining tabs are handled with the appropriate tab references
        if performance_summary:
            # Performance tests were run, so tab indices are shifted
            with tab3:  # Passed Tests tab
                if analysis['passed_tests']:
                    st.dataframe(
                        pd.DataFrame(analysis['passed_tests']),
                        use_container_width=True
                    )
                else:
                    st.info("No passed tests to display")
            
            with tab4:  # Failed Tests tab
                if analysis['failed_tests']:
                    st.dataframe(
                        pd.DataFrame(analysis['failed_tests']),
                        use_container_width=True
                    )
                else:
                    st.success("No failed tests! 🎉")
            
            with tab5:  # Raw Data tab
                st.json(analysis['raw_data'])
        else:
            # No performance tests, normal tab indices
            with tab2:  # Passed Tests tab
                if analysis['passed_tests']:
                    st.dataframe(
                        pd.DataFrame(analysis['passed_tests']),
                        use_container_width=True
                    )
                else:
                    st.info("No passed tests to display")
            
            with tab3:  # Failed Tests tab
                if analysis['failed_tests']:
                    st.dataframe(
                        pd.DataFrame(analysis['failed_tests']),
                        use_container_width=True
                    )
                else:
                    st.success("No failed tests! 🎉")
            
            with tab4:  # Raw Data tab
                st.json(analysis['raw_data'])
    
    # Download results
    st.subheader("📥 Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download - exclude non-serializable objects like Plotly figures
        def is_json_serializable(obj):
            """Check if an object is JSON serializable."""
            try:
                json.dumps(obj)
                return True
            except (TypeError, OverflowError):
                return False
        
        json_analysis = {key: value for key, value in analysis.items() 
                        if is_json_serializable(value)}
        json_data = json.dumps(json_analysis, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=json_data,
            file_name="api_test_results.json",
            mime="application/json"
        )
    
    with col2:
        # CSV download
        if analysis.get('csv_data'):
            st.download_button(
                label="Download CSV Report",
                data=analysis['csv_data'],
                file_name="api_test_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
