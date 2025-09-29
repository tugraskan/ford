#!/usr/bin/env python3

from ford.sourceform import IoTracker

def test_variable_defaults():
    # Test the variable defaults extraction
    tracker = IoTracker()
    
    # Sample Fortran source code lines
    source_lines = [
        '      subroutine test_procedure',
        '      ',
        '      implicit none',
        '      ',
        '      character(len=100) :: filename = ""',
        '      integer :: unit_num = 107',
        '      ',
        '      ! Set default file names',
        '      in_link%aqu_cha = "aqu_cha.lin"',
        '      in_hru%hru_data = "hru_data.hru"',
        '      filename = "test_data.txt"',
        '      ',
        '      open(107, file=in_link%aqu_cha)',
        '      read(107, *) data',
        '      close(107)',
        '      ',
        '      end subroutine'
    ]
    
    # Extract variable defaults
    defaults = tracker.extract_variable_defaults(source_lines)
    
    print("Extracted variable defaults:")
    for var_name, var_value in defaults.items():
        print(f"  {var_name} = {var_value}")
    
    # Test finding relevant defaults for an operation
    operation = {
        'kind': 'open',
        'raw': 'open(107, file=in_link%aqu_cha)',
        'line': 13
    }
    
    relevant = tracker._find_relevant_variable_defaults(operation, defaults)
    print("\nRelevant defaults for operation:", operation['raw'])
    for var_name, var_value in relevant.items():
        print(f"  {var_name} = {var_value}")

if __name__ == "__main__":
    test_variable_defaults()