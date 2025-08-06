# API Testing Suite - Quick Start Guide

## 🚀 Getting Started

Your API Testing Suite is now ready! Here are three ways to launch the application:

### Option 1: VS Code Task (Recommended)
1. Press `Ctrl+Shift+P` to open the command palette
2. Type "Tasks: Run Task"
3. Select "Setup and Run API Testing Suite"
4. The application will start automatically

### Option 2: Launch Script (Python)
```bash
python launch.py
```

### Option 3: Batch File (Windows)
Double-click on `launch.bat` or run it from the terminal:
```cmd
launch.bat
```

## 📖 How to Use

1. **Start the Application**: Use any of the launch methods above
2. **Open Browser**: Navigate to `http://localhost:8501` (should open automatically)
3. **Upload API Spec**: 
   - Upload a `.yaml`, `.yml`, or `.json` OpenAPI/Swagger file
   - Or paste your API specification directly
4. **Configure Tests**: Set your preferences in the sidebar
5. **Run Tests**: Click "🚀 Generate and Execute Tests"
6. **Analyze Results**: Review the comprehensive test reports

## 📁 Project Structure

```
c:\Tools\API\test-suite\
├── app.py                    # Main Streamlit application
├── launch.py                 # Python launch script
├── launch.bat               # Windows batch launcher
├── config.py                # Application configuration
├── requirements.txt         # Python dependencies
├── README.md               # Detailed documentation
├── .venv/                  # Virtual environment (auto-created)
├── modules/                # Core application modules
│   ├── swagger_parser.py   # API spec parser
│   ├── test_generator.py   # Test case generator
│   ├── request_executor.py # HTTP request executor
│   └── results_analyzer.py # Results analysis
├── examples/               # Sample API specifications
│   ├── petstore-api.yaml   # Pet store API example
│   └── user-management-api.json # User API example
└── tests/                  # Unit tests
    └── test_modules.py     # Test suite
```

## 🧪 Example API Specifications

We've included two example API specifications you can use to test the application:

1. **Pet Store API** (`examples/petstore-api.yaml`)
   - Simple CRUD operations for pets
   - Demonstrates path parameters, query parameters, and request bodies

2. **User Management API** (`examples/user-management-api.json`)
   - More complex user management system
   - Includes authentication, pagination, and validation

## ⚙️ Configuration Options

### Test Settings
- **Requests per endpoint**: 1-1000 (default: 10)
- **Concurrent requests**: 1-50 (default: 5)
- **Request timeout**: 1-300 seconds (default: 30)

### Test Types
- ✅ **Valid data tests**: Test with expected, valid data
- ❌ **Invalid data tests**: Test with malformed/invalid data
- 🔍 **Edge case tests**: Boundary conditions and special cases
- 🔒 **Security tests**: Basic security vulnerability testing
- ⚡ **Performance tests**: Load testing capabilities

## 📊 What You'll Get

### Comprehensive Analytics
- Success/failure rates
- Response time statistics
- HTTP status code distribution
- Error analysis and categorization

### Interactive Visualizations
- Response time charts
- Performance trends
- Status code breakdowns

### Export Options
- JSON reports with full test data
- CSV exports for spreadsheet analysis
- Downloadable charts and graphs

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Run the setup again: `python launch.py`
   - Check that virtual environment is activated

2. **Port already in use**
   - Stop any existing Streamlit processes
   - Try a different port: `streamlit run app.py --server.port 8502`

3. **Python not found**
   - Ensure Python 3.8+ is installed and in your PATH
   - Try using `python3` instead of `python`

### Need Help?
- Check the detailed README.md file
- Review the example API specifications
- Run the unit tests: `python -m pytest tests/`

## 🎯 Next Steps

1. **Test with your own API**: Upload your OpenAPI specification
2. **Customize test scenarios**: Modify the test generator for specific needs
3. **Integrate with CI/CD**: Use the JSON reports in your automation pipelines
4. **Scale up**: Increase concurrent requests for load testing

---

**Happy Testing! 🧪**

The application should now be running at: http://localhost:8501
