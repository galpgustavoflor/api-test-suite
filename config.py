# Configuration file for API Testing Suite

# Default settings for the application
default_config = {
    "app": {
        "title": "API Testing Suite",
        "page_icon": "🧪",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    },
    "testing": {
        "default_num_requests": 10,
        "max_num_requests": 1000,
        "default_concurrent_requests": 5,
        "max_concurrent_requests": 50,
        "default_timeout": 30,
        "max_timeout": 300,
        "default_test_types": {
            "valid_data": True,
            "invalid_data": True,
            "edge_cases": True,
            "security": False,
            "performance": False
        }
    },
    "ui": {
        "show_debug_info": False,
        "max_response_body_length": 1000,
        "chart_height": 400,
        "table_height": 300
    },
    "export": {
        "json_indent": 2,
        "csv_separator": ",",
        "include_response_body": True
    }
}

# Environment-specific configurations
development_config = {
    **default_config,
    "ui": {
        **default_config["ui"],
        "show_debug_info": True
    },
    "testing": {
        **default_config["testing"],
        "default_timeout": 60
    }
}

production_config = {
    **default_config,
    "testing": {
        **default_config["testing"],
        "max_concurrent_requests": 20,
        "default_timeout": 15
    }
}

def get_config(environment="default"):
    """
    Get configuration based on environment.
    
    Args:
        environment: Configuration environment (default, development, production)
        
    Returns:
        Configuration dictionary
    """
    configs = {
        "default": default_config,
        "development": development_config,
        "production": production_config
    }
    
    return configs.get(environment, default_config)
