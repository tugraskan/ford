"""
Tests for the create_header_table filter function
"""
import pytest
from ford.output import create_header_table
from ford.sourceform import FortranType, FortranVariable


class MockVariable:
    """Mock FortranVariable for testing"""
    def __init__(self, name, vartype, initial=None, kind=None, strlen=None):
        self.name = name
        self.vartype = vartype
        self.initial = initial
        self.kind = kind
        self.strlen = strlen
    
    @property
    def full_type(self):
        """Return the full type, including kind, len, etc."""
        result = self.vartype
        parameter_parts = []
        
        if self.kind:
            parameter_parts.append(f"kind={self.kind}")
        if self.strlen:
            parameter_parts.append(f"len={self.strlen}")
        
        if parameter_parts:
            result += f"({', '.join(parameter_parts)})"
        
        return result


class MockType:
    """Mock FortranType for testing"""
    def __init__(self, name, variables):
        self.name = name
        self.variables = variables


def test_create_header_table_basic():
    """Test creating a basic header table with a few fields"""
    # Create mock type with components
    var1 = MockVariable("day", "character", initial='"  jday"', strlen="6")
    var2 = MockVariable("mo", "character", initial='" mon"', strlen="6")
    var3 = MockVariable("dep_wt", "character", initial='" dep_wt"', strlen="16")
    
    mock_type = MockType("aqu_header_units", [var1, var2, var3])
    
    # Create header table
    result = create_header_table(mock_type, "aqu_header_units")
    
    # Check result
    assert result is not None
    assert len(result['fields']) == 3
    assert result['fields'] == ['day', 'mo', 'dep_wt']
    assert result['attributes'] == ['aqu_header_units%day', 'aqu_header_units%mo', 'aqu_header_units%dep_wt']
    assert result['names'] == ['day', 'mo', 'dep_wt']
    assert result['initials'] == ['"  jday"', '" mon"', '" dep_wt"']
    assert result['types'] == ['character(len=6)', 'character(len=6)', 'character(len=16)']


def test_create_header_table_with_proto():
    """Test creating header table from a variable with proto"""
    # Create mock variable components
    var1 = MockVariable("day", "character", initial='"  jday"', strlen="6")
    var2 = MockVariable("mo", "character", initial='" mon"', strlen="6")
    
    mock_type = MockType("aqu_header_units", [var1, var2])
    
    # Create a variable that has this type as proto
    class MockVarWithProto:
        def __init__(self):
            self.proto = [mock_type]
    
    var_with_proto = MockVarWithProto()
    
    # Create header table
    result = create_header_table(var_with_proto, "aqu_header_units")
    
    # Check result
    assert result is not None
    assert len(result['fields']) == 2
    assert result['fields'] == ['day', 'mo']


def test_create_header_table_empty_type():
    """Test creating header table from empty type"""
    mock_type = MockType("empty_type", [])
    result = create_header_table(mock_type)
    assert result is None


def test_create_header_table_no_initial():
    """Test creating header table when variables have no initial values"""
    var1 = MockVariable("day", "character", strlen="6")
    var2 = MockVariable("mo", "character", strlen="6")
    
    mock_type = MockType("test_type", [var1, var2])
    result = create_header_table(mock_type)
    
    assert result is not None
    assert result['initials'] == ['', '']


def test_create_header_table_none_input():
    """Test creating header table with None input"""
    result = create_header_table(None)
    assert result is None


def test_create_header_table_infer_parent_name():
    """Test that parent type name is inferred from type if not provided"""
    var1 = MockVariable("day", "character", initial='"  jday"', strlen="6")
    mock_type = MockType("inferred_type", [var1])
    
    result = create_header_table(mock_type)
    
    assert result is not None
    assert result['attributes'] == ['inferred_type%day']
