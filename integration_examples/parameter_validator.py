#!/usr/bin/env python3
"""
Parameter validation script generated from FORD Modular Database
"""

def validate_parameters(param_dict):
    """Validate parameters using FORD database rules"""
    from modular_database_demo import ModularDatabaseAPI
    
    api = ModularDatabaseAPI()
    results = {}
    
    for param_name, value in param_dict.items():
        result = api.validate_parameter_value(param_name, str(value))
        results[param_name] = result
    
    return results

if __name__ == '__main__':
    # Example usage
    test_params = {
        'area': '100.5',
        'invalid_param': 'test'
    }
    
    results = validate_parameters(test_params)
    for param, result in results.items():
        status = "✓" if result['valid'] else "✗"
        print(f"{param}: {status}")
