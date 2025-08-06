<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# API Testing Suite - Copilot Instructions

This is a Python-based Streamlit application for comprehensive API testing using Swagger/OpenAPI specifications.

## Project Overview
- **Framework**: Streamlit for web interface
- **Purpose**: Massive API testing and quality assurance
- **Key Features**: Test generation, concurrent execution, analytics, reporting

## Code Style and Conventions
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write comprehensive docstrings for all functions and classes
- Use descriptive variable and function names
- Keep functions focused and modular

## Architecture Patterns
- **Modular Design**: Separate concerns into distinct modules
- **Single Responsibility**: Each class/function has one clear purpose
- **Error Handling**: Implement robust error handling and logging
- **Async Support**: Use asyncio/aiohttp for concurrent operations

## Key Technologies
- `streamlit`: Web interface framework
- `requests`/`aiohttp`: HTTP client libraries
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations
- `pyyaml`: YAML parsing
- `faker`: Test data generation

## Testing Approach
- Generate comprehensive test cases from OpenAPI specs
- Support multiple test types: valid, invalid, edge cases, security
- Implement concurrent test execution
- Provide detailed analytics and reporting

## Best Practices
- Validate all inputs before processing
- Handle API specification parsing errors gracefully
- Implement proper timeout and retry mechanisms
- Generate meaningful test data using schemas
- Provide clear user feedback and progress indicators

## Security Considerations
- Disable SSL verification for testing environments only
- Implement basic security test cases
- Handle sensitive data appropriately
- Validate all user inputs

When generating code, ensure compatibility with the existing architecture and maintain consistency with the established patterns.
