# 🧪 API Testing Suite

A comprehensive Streamlit-based application for massive API testing based on Swagger/OpenAPI specifications. This tool automatically generates and executes comprehensive test cases for REST APIs to ensure quality assurance.

## ✨ Features

- **📄 Multiple Input Methods**: Upload Swagger/OpenAPI files or paste YAML/JSON specifications directly
- **🎯 Comprehensive Test Generation**: Automatically generates various test types:
  - ✅ Valid data tests
  - ❌ Invalid data tests  
  - 🔍 Edge case tests
  - 🔒 Security tests
  - ⚡ Performance/Load tests
- **🚀 Concurrent Execution**: Configurable concurrent request execution for faster testing
- **📊 Rich Analytics**: Detailed performance metrics, success rates, and error analysis
- **📈 Interactive Visualizations**: Charts and graphs for test results analysis
- **💾 Export Results**: Download test results in JSON and CSV formats
- **🎨 User-Friendly Interface**: Clean, intuitive Streamlit interface

## 🛠️ Installation

1. **Clone or create the project directory**:
   ```bash
   cd c:\Tools\API\test-suite
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 🚀 Usage

### 1. **Input API Specification**
   - **Upload File**: Choose a `.yaml`, `.yml`, or `.json` OpenAPI/Swagger file
   - **Paste Content**: Copy and paste your API specification directly

### 2. **Configure Tests**
   - Set number of requests per endpoint (1-1000)
   - Configure concurrent requests (1-50)
   - Set request timeout
   - Choose test types to run

### 3. **Execute Tests**
   - Click "🚀 Generate and Execute Tests"
   - Monitor progress and view real-time results
   - Analyze comprehensive test reports

### 4. **Review Results**
   - **📈 Overview**: Performance charts and status code distribution
   - **✅ Passed Tests**: List of successful test cases
   - **❌ Failed Tests**: Detailed failure analysis
   - **📋 Raw Data**: Complete test result data

### 5. **Export Results**
   - Download JSON reports for detailed analysis
   - Export CSV files for spreadsheet analysis

## 📁 Project Structure

```
c:\Tools\API\test-suite\
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── modules/                  # Core application modules
│   ├── __init__.py          # Package initialization
│   ├── swagger_parser.py     # OpenAPI/Swagger specification parser
│   ├── test_generator.py     # Test case generator
│   ├── request_executor.py   # HTTP request executor with concurrency
│   └── results_analyzer.py   # Test results analysis and reporting
├── examples/                 # Example API specifications
├── tests/                   # Unit tests
└── .vscode/                 # VS Code configuration
    └── tasks.json           # Build and run tasks
```

## 🔧 Configuration Options

### Test Settings
- **Number of requests per endpoint**: 1-1000 requests
- **Concurrent requests**: 1-50 simultaneous requests
- **Request timeout**: 1-60 seconds

### Test Types
- **Valid data tests**: Test with valid, expected data
- **Invalid data tests**: Test with invalid parameters and data
- **Edge case tests**: Test boundary conditions and special cases
- **Security tests**: Basic security vulnerability testing
- **Performance tests**: Load and stress testing capabilities

## 📊 Generated Test Types

### Valid Data Tests
- Tests with properly formatted, valid data
- Uses example values from API specification
- Tests happy path scenarios

### Invalid Data Tests
- Missing required parameters
- Invalid data types
- Malformed request bodies
- Out-of-range values

### Edge Case Tests
- Empty request bodies
- Maximum length strings
- Special characters and encoding
- Boundary value testing

### Security Tests
- Authentication bypass attempts
- SQL injection attempts
- XSS payload testing
- Invalid token testing

## 📈 Analytics & Reporting

### Summary Metrics
- Total tests executed
- Success/failure rates
- Average response times
- Performance percentiles (95th, 99th)

### Detailed Analysis
- Response time distribution charts
- HTTP status code analysis
- Error categorization and patterns
- Endpoint-specific performance metrics

### Export Options
- **JSON Reports**: Complete test data with metadata
- **CSV Exports**: Tabular data for analysis tools
- **Performance Charts**: Visual performance analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) section
2. Create a new issue with detailed information
3. Include your API specification (if possible) and error messages

## 🚀 Roadmap

- [ ] **API Mocking**: Built-in mock server for testing
- [ ] **Test Scheduling**: Automated recurring test execution
- [ ] **Advanced Security Tests**: OWASP top 10 security testing
- [ ] **Custom Test Scripts**: User-defined test logic
- [ ] **CI/CD Integration**: GitHub Actions, Jenkins integration
- [ ] **Multi-Environment Support**: Dev, staging, production testing
- [ ] **Historical Reporting**: Trend analysis over time
- [ ] **Team Collaboration**: Shared test suites and results

## 🏷️ Tags

`api-testing` `swagger` `openapi` `streamlit` `python` `qa` `automation` `testing` `rest-api` `load-testing`
