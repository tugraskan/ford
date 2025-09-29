#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.sourceform import FortranProcedure, FortranVariable

# Create a mock procedure to test the properties
class MockProcedure:
    def __init__(self):
        self.name = "basin_print_codes_read"
        self.variables = []
        self.args = []
        self.uses = []
        
        # Add some mock local variables
        var1 = MockVariable("header", "character(len=500)", self)
        var2 = MockVariable("titldum", "character(len=80)", self)
        var3 = MockVariable("eof", "integer", self)
        
        self.variables = [var1, var2, var3]
        
        # Add some mock uses (modules)
        self.uses = [
            (MockModule("input_file_module"), "only", "in_sim"),
            (MockModule("basin_module"), "only", "pco"),
            (MockModule("time_module"),)
        ]
    
    @property
    def local_variables(self):
        """Return variables that are declared locally within this procedure (excluding arguments)."""
        local_vars = []
        
        # Get variables that are declared in this procedure
        if hasattr(self, 'variables'):
            for var in self.variables:
                # Variable is local if its parent is this procedure
                if getattr(var, 'parent', None) == self:
                    local_vars.append(var)
        
        return local_vars

    @property 
    def non_local_variables(self):
        """Return variables that are not declared locally (arguments, parameters, etc.)."""
        non_local_vars = []
        
        # Include arguments
        if hasattr(self, 'args'):
            non_local_vars.extend(self.args)
        
        # Include variables that are not local to this procedure
        if hasattr(self, 'variables'):
            for var in self.variables:
                if getattr(var, 'parent', None) != self:
                    non_local_vars.append(var)
        
        return non_local_vars

    @property
    def outside_variables_used(self):
        """Return variables and types from outside modules that are used in this procedure."""
        outside_vars = []
        
        # Get variables from uses
        if hasattr(self, 'uses'):
            for use in self.uses:
                # Ensure use is a sequence (list/tuple) before checking length
                if isinstance(use, (list, tuple)) and len(use) > 1 and hasattr(use[0], 'variables'):
                    # If specific items are imported
                    if len(use) > 2:
                        for item_name in use[2:]:
                            for var in use[0].variables:
                                if var.name.lower() == item_name.lower():
                                    outside_vars.append(var)
                    else:
                        # If whole module is used
                        outside_vars.extend(use[0].variables)
        
        # Remove duplicates by name
        seen_names = set()
        unique_vars = []
        for var in outside_vars:
            if var.name.lower() not in seen_names:
                seen_names.add(var.name.lower())
                unique_vars.append(var)
        
        return unique_vars

class MockVariable:
    def __init__(self, name, var_type, parent):
        self.name = name
        self.var_type = var_type
        self.parent = parent

class MockModule:
    def __init__(self, name):
        self.name = name
        self.variables = [
            MockVariable("in_sim", "type(file_pointer)", None),
            MockVariable("pco", "type(print_control)", None),
            MockVariable("time", "type(time_class)", None),
        ]

# Test the properties
proc = MockProcedure()

print("Testing procedure properties:")
print(f"Procedure name: {proc.name}")
print(f"Total variables: {len(proc.variables)}")
print(f"Local variables: {len(proc.local_variables)}")
print(f"Non-local variables: {len(proc.non_local_variables)}")
print(f"Outside variables used: {len(proc.outside_variables_used)}")

print("\nLocal variables:")
for var in proc.local_variables:
    print(f"  - {var.name}: {var.var_type}")

print("\nOutside variables used:")
for var in proc.outside_variables_used:
    print(f"  - {var.name}: {var.var_type}")