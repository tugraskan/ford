#!/usr/bin/env python3

"""Test variable defaults extraction functionality."""

import sys
import os
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.sourceform import IoTracker

def test_variable_defaults():
    """Test the variable defaults extraction and association."""
    
    # Create a test source for input_file_module
    module_source = [
        "module input_file_module",
        "  implicit none",
        "  type input_sim",
        '    character(len=25) :: prt = "print.prt"',
        '    character(len=25) :: time = "time.sim"',
        "  end type input_sim",
        "  type (input_sim) :: in_sim",
        "end module input_file_module"
    ]
    
    # Create a test source for a procedure that uses the module
    procedure_source = [
        "subroutine test_procedure",
        "  use input_file_module",
        "  implicit none",
        "  integer :: eof = 0",
        "  open (107,file=in_sim%prt)",
        "  read (107,*,iostat=eof) header",
        "  close (107)",
        "end subroutine test_procedure"
    ]
    
    # Test variable defaults extraction from module
    tracker = IoTracker()
    module_defaults = tracker.extract_variable_defaults(module_source)
    print("Module defaults extracted:")
    for var, val in module_defaults.items():
        print(f"  {var} = {val}")
    
    # Test variable defaults extraction from procedure
    procedure_defaults = tracker.extract_variable_defaults(procedure_source)
    print("\nProcedure defaults extracted:")
    for var, val in procedure_defaults.items():
        print(f"  {var} = {val}")
    
    # Combine defaults
    all_defaults = {**module_defaults, **procedure_defaults}
    print(f"\nAll defaults: {all_defaults}")
    
    # Test association logic
    test_operation = {
        'kind': 'open',
        'raw': 'open (107,file=in_sim%prt)',
        'line': 5
    }
    
    relevant_defaults = tracker._find_relevant_variable_defaults(test_operation, all_defaults)
    print(f"\nRelevant defaults for 'open (107,file=in_sim%prt)': {relevant_defaults}")
    
    return len(relevant_defaults) > 0

if __name__ == "__main__":
    success = test_variable_defaults()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")