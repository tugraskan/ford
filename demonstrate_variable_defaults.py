#!/usr/bin/env python3

# Test script to demonstrate that variable defaults functionality is working

from ford.sourceform import IoTracker

def demonstrate_variable_defaults():
    print("=== Variable Defaults Functionality Test ===\n")
    
    # Create IoTracker instance
    tracker = IoTracker()
    
    # Sample Fortran source that shows variable assignments like the user requested
    fortran_source = [
        'subroutine example_with_defaults',
        '',
        'implicit none',
        '',
        'character(len=100) :: filename',
        'integer :: unit_num = 107',
        '',
        '! Set default file names as requested by user',
        'in_link%aqu_cha = "aqu_cha.lin"',
        'in_hru%hru_data = "hru_data.hru"', 
        'filename = "test_output.txt"',
        '',
        'open(107, file=in_link%aqu_cha)',
        'read(107, *) data',
        'write(108, file=filename) result',
        'close(107)',
        '',
        'end subroutine'
    ]
    
    print("1. Extract variable defaults from source:")
    defaults = tracker.extract_variable_defaults(fortran_source)
    for var_name, var_value in defaults.items():
        print(f"   {var_name} = {var_value}")
    
    print("\n2. Test I/O operations with variable defaults:")
    
    # Simulate I/O operations that would be found in the code
    operations = [
        {
            'kind': 'open',
            'raw': 'open(107, file=in_link%aqu_cha)',
            'line': 13,
            'condition': None
        },
        {
            'kind': 'read', 
            'raw': 'read(107, *) data',
            'line': 14,
            'condition': None
        },
        {
            'kind': 'write',
            'raw': 'write(108, file=filename) result', 
            'line': 15,
            'condition': None
        }
    ]
    
    # Test finding relevant defaults for each operation
    for op in operations:
        relevant = tracker._find_relevant_variable_defaults(op, defaults)
        print(f"\n   Operation: {op['raw']}")
        if relevant:
            print("   Variable defaults found:")
            for var_name, var_value in relevant.items():
                print(f"     {var_name} = {var_value}")
        else:
            print("   No relevant variable defaults found")
    
    print("\n3. Expected HTML output would show:")
    print("   - I/O Operations table with 'Variable Defaults' column")
    print("   - Operations showing associated variable assignments")
    print("   - Example: open(107, file=in_link%aqu_cha) would show 'in_link%aqu_cha = aqu_cha.lin'")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    demonstrate_variable_defaults()