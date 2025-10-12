"""
Tests for the FORD comparison module (ford.compare)
"""

import json
import pytest
from pathlib import Path
from ford.compare import (
    load_metadata,
    extract_module_names,
    extract_procedure_names,
    extract_type_names,
    compare_metadata,
    ComparisonResult,
    format_report,
)


@pytest.fixture
def sample_metadata_v1():
    """Sample metadata representing version 1 of a project"""
    return {
        "ford-metadata": {"version": "1.0.0"},
        "modules": [
            {
                "name": "module_a",
                "obj": "module",
                "external_url": "./module/module_a.html",
                "functions": [
                    {"name": "func1", "obj": "function"},
                    {"name": "func2", "obj": "function"},
                ],
                "subroutines": [
                    {
                        "name": "sub1", 
                        "obj": "subroutine",
                        "args": [
                            {"name": "input", "vartype": "type(type_a)"}
                        ]
                    },
                ],
                "types": [
                    {"name": "type_a", "obj": "type"},
                ],
                "variables": [
                    {"name": "var1", "obj": "variable"},
                ],
                "pub_vars": [
                    {"name": "var1", "obj": "variable"},
                ],
            },
            {
                "name": "module_b",
                "obj": "module",
                "external_url": "./module/module_b.html",
                "functions": [
                    {"name": "funcB", "obj": "function"},
                ],
                "subroutines": [],
                "types": [],
                "variables": [],
            },
        ],
        "metadata": [],
    }


@pytest.fixture
def sample_metadata_v2():
    """Sample metadata representing version 2 of a project with changes"""
    return {
        "ford-metadata": {"version": "1.0.0"},
        "modules": [
            {
                "name": "module_a",
                "obj": "module",
                "external_url": "./module/module_a.html",
                "functions": [
                    {"name": "func1", "obj": "function"},
                    # func2 removed
                    {"name": "func3", "obj": "function"},  # new function
                ],
                "subroutines": [
                    {
                        "name": "sub1", 
                        "obj": "subroutine",
                        "args": [
                            {"name": "input", "vartype": "type(type_a)"}
                        ]
                    },
                    {
                        "name": "sub2", 
                        "obj": "subroutine",  # new subroutine
                        "args": [
                            {"name": "data", "vartype": "type(type_b)"}
                        ]
                    },
                ],
                "types": [
                    {"name": "type_a", "obj": "type"},
                    {"name": "type_b", "obj": "type"},  # new type
                ],
                "variables": [
                    {"name": "var1", "obj": "variable"},
                    {"name": "var2", "obj": "variable"},  # new variable
                ],
                "pub_vars": [
                    {"name": "var1", "obj": "variable"},
                    {"name": "var2", "obj": "variable"},
                ],
            },
            # module_b removed
            {
                "name": "module_c",  # new module
                "obj": "module",
                "external_url": "./module/module_c.html",
                "functions": [],
                "subroutines": [
                    {"name": "subC", "obj": "subroutine"},
                ],
                "types": [],
                "variables": [],
            },
        ],
        "metadata": [],
    }


def test_load_metadata(tmp_path):
    """Test loading metadata from JSON file"""
    # Create a test JSON file
    test_data = {"modules": [], "metadata": []}
    test_file = tmp_path / "test_modules.json"
    test_file.write_text(json.dumps(test_data))
    
    # Load the metadata
    result = load_metadata(test_file)
    
    assert result == test_data
    assert "modules" in result
    assert "metadata" in result


def test_load_metadata_file_not_found():
    """Test that loading non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        load_metadata(Path("/nonexistent/file.json"))


def test_extract_module_names(sample_metadata_v1):
    """Test extracting module names from metadata"""
    modules = extract_module_names(sample_metadata_v1)
    
    assert modules == {"module_a", "module_b"}


def test_extract_procedure_names(sample_metadata_v1):
    """Test extracting procedure names from metadata"""
    procedures = extract_procedure_names(sample_metadata_v1)
    
    expected = {
        "module_a::func1",
        "module_a::func2",
        "module_a::sub1",
        "module_b::funcB",
    }
    assert procedures == expected


def test_extract_type_names(sample_metadata_v1):
    """Test extracting type names used in procedure arguments from metadata"""
    types = extract_type_names(sample_metadata_v1)
    
    # Only type_a is extracted because it's used in sub1's arguments
    assert types == {"module_a::type_a"}


def test_compare_metadata_modules(sample_metadata_v1, sample_metadata_v2):
    """Test comparison of modules between versions"""
    result = compare_metadata(sample_metadata_v1, sample_metadata_v2)
    
    # module_c is new, module_b is removed, module_a exists in both
    assert result.new_modules == {"module_c"}
    assert result.removed_modules == {"module_b"}


def test_compare_metadata_procedures(sample_metadata_v1, sample_metadata_v2):
    """Test comparison of procedures between versions"""
    result = compare_metadata(sample_metadata_v1, sample_metadata_v2)
    
    # New procedures: func3, sub2, subC
    expected_new = {"module_a::func3", "module_a::sub2", "module_c::subC"}
    assert result.new_procedures == expected_new
    
    # Removed procedures: func2, funcB (in removed module)
    expected_removed = {"module_a::func2", "module_b::funcB"}
    assert result.removed_procedures == expected_removed


def test_compare_metadata_types(sample_metadata_v1, sample_metadata_v2):
    """Test comparison of derived types between versions"""
    result = compare_metadata(sample_metadata_v1, sample_metadata_v2)
    
    assert result.new_types == {"module_a::type_b"}
    assert result.removed_types == set()


def test_format_report(sample_metadata_v1, sample_metadata_v2):
    """Test report formatting"""
    result = compare_metadata(sample_metadata_v1, sample_metadata_v2)
    report = format_report(result, verbose=False)
    
    # Check that report contains expected sections
    assert "MODULES" in report
    assert "PROCEDURES" in report
    assert "DERIVED TYPES" in report
    assert "SUMMARY" in report
    
    # Check that specific changes are mentioned
    assert "module_c" in report
    assert "module_b" in report


def test_format_report_verbose(sample_metadata_v1, sample_metadata_v2):
    """Test verbose report formatting includes variables"""
    result = compare_metadata(sample_metadata_v1, sample_metadata_v2)
    report = format_report(result, verbose=True)
    
    # Verbose report should include variables section
    assert "VARIABLES" in report


def test_compare_metadata_no_changes():
    """Test comparison with no changes"""
    metadata = {
        "modules": [
            {
                "name": "module_x",
                "functions": [],
                "subroutines": [],
                "types": [],
                "variables": [],
            }
        ]
    }
    
    result = compare_metadata(metadata, metadata)
    
    # No changes should be detected
    assert len(result.new_modules) == 0
    assert len(result.removed_modules) == 0
    assert len(result.new_procedures) == 0
    assert len(result.removed_procedures) == 0


def test_compare_empty_metadata():
    """Test comparison with empty metadata"""
    empty = {"modules": []}
    
    result = compare_metadata(empty, empty)
    
    assert len(result.new_modules) == 0
    assert len(result.removed_modules) == 0


def test_comparison_result_dataclass():
    """Test ComparisonResult dataclass initialization"""
    result = ComparisonResult()
    
    assert isinstance(result.new_modules, set)
    assert isinstance(result.removed_modules, set)
    assert isinstance(result.new_procedures, set)
    assert isinstance(result.removed_procedures, set)
    assert len(result.new_modules) == 0


def test_extract_names_with_none_values():
    """Test extraction functions handle None values gracefully"""
    metadata_with_nones = {
        "modules": [
            None,  # None module
            {
                "name": "valid_module",
                "functions": [None, {"name": "func1"}],
                "subroutines": [],
                "types": [],
                "variables": [],
            },
        ]
    }
    
    # Should not raise an exception
    modules = extract_module_names(metadata_with_nones)
    assert modules == {"valid_module"}
    
    procedures = extract_procedure_names(metadata_with_nones)
    assert procedures == {"valid_module::func1"}


def test_extract_names_missing_keys():
    """Test extraction functions handle missing keys"""
    metadata_minimal = {
        "modules": [
            {"name": "minimal_module"}  # Missing functions, subroutines, etc.
        ]
    }
    
    # Should not raise an exception
    modules = extract_module_names(metadata_minimal)
    assert modules == {"minimal_module"}
    
    procedures = extract_procedure_names(metadata_minimal)
    assert len(procedures) == 0
