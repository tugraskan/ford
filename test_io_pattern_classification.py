"""
Test pure I/O pattern-based classification (no filename keywords).
"""

import sys
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.sourceform import FortranIOFile


def test_connect_file_looped_reads():
    """Test that files with looped reads are classified as Connect."""
    iofile = FortranIOFile("test_file.txt", "10")
    
    # Simulate looped reads with consistent structure
    # Like: DO i=1,n; READ(10,*) hru_id, channel_id, aquifer_id; END DO
    for i in range(10):
        iofile.operations.append({
            "kind": "read",
            "raw": f"READ(10,*) hru_id, channel_id, aquifer_id",
            "parameters": ["hru_id", "channel_id", "aquifer_id"],
            "condition": "i",  # Inside loop
            "condition_stack": ["DO i=1,n"],
            "is_probe_read": False
        })
    
    classification = iofile.file_classification
    print(f"Looped reads test: {classification}")
    assert classification == "Connect", f"Expected 'Connect', got '{classification}'"
    print("✓ Test passed: Looped reads classified as Connect")


def test_simple_file_sequential_reads():
    """Test that files with sequential consistent reads are classified as Simple."""
    iofile = FortranIOFile("test_file.txt", "10")
    
    # Simulate sequential reads with consistent structure (no loops)
    for i in range(5):
        iofile.operations.append({
            "kind": "read",
            "raw": f"READ(10,*) date, temp, precip",
            "parameters": ["date", "temp", "precip"],
            "condition": None,  # Not in loop
            "condition_stack": None,
            "is_probe_read": False
        })
    
    classification = iofile.file_classification
    print(f"Sequential reads test: {classification}")
    assert classification == "Simple", f"Expected 'Simple', got '{classification}'"
    print("✓ Test passed: Sequential reads classified as Simple")


def test_unique_file_variable_structure():
    """Test that files with variable structure are classified as Unique."""
    iofile = FortranIOFile("test_file.txt", "10")
    
    # Simulate variable structure (different columns per read)
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) header",
        "parameters": ["header"],
        "condition": None,
        "is_probe_read": False
    })
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) version, date, author",
        "parameters": ["version", "date", "author"],
        "condition": None,
        "is_probe_read": False
    })
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) setting1, setting2",
        "parameters": ["setting1", "setting2"],
        "condition": None,
        "is_probe_read": False
    })
    
    classification = iofile.file_classification
    print(f"Variable structure test: {classification}")
    assert classification == "Unique", f"Expected 'Unique', got '{classification}'"
    print("✓ Test passed: Variable structure classified as Unique")


def test_unique_file_probe_reads():
    """Test that files with probe reads are classified as Unique."""
    iofile = FortranIOFile("test_file.txt", "10")
    
    # Simulate probe read (test read followed by rewind)
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) test_var",
        "parameters": ["test_var"],
        "condition": None,
        "is_probe_read": True  # Marked as probe read
    })
    iofile.operations.append({
        "kind": "rewind",
        "raw": "REWIND(10)",
        "parameters": [],
        "condition": None,
        "is_probe_read": False
    })
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) actual_data",
        "parameters": ["actual_data"],
        "condition": None,
        "is_probe_read": False
    })
    
    classification = iofile.file_classification
    print(f"Probe reads test: {classification}")
    assert classification == "Unique", f"Expected 'Unique', got '{classification}'"
    print("✓ Test passed: Probe reads classified as Unique")


def test_unique_file_complex_positioning():
    """Test that files with complex positioning are classified as Unique."""
    iofile = FortranIOFile("test_file.txt", "10")
    
    # Simulate complex positioning with rewind
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) config",
        "parameters": ["config"],
        "condition": None,
        "is_probe_read": False
    })
    iofile.operations.append({
        "kind": "rewind",
        "raw": "REWIND(10)",
        "parameters": [],
        "condition": None,
        "is_probe_read": False
    })
    iofile.operations.append({
        "kind": "read",
        "raw": "READ(10,*) settings",
        "parameters": ["settings"],
        "condition": None,
        "is_probe_read": False
    })
    
    classification = iofile.file_classification
    print(f"Complex positioning test: {classification}")
    assert classification == "Unique", f"Expected 'Unique', got '{classification}'"
    print("✓ Test passed: Complex positioning classified as Unique")


if __name__ == "__main__":
    print("Testing pure I/O pattern-based classification (no filename keywords)")
    print("=" * 70)
    
    test_connect_file_looped_reads()
    test_simple_file_sequential_reads()
    test_unique_file_variable_structure()
    test_unique_file_probe_reads()
    test_unique_file_complex_positioning()
    
    print("=" * 70)
    print("All tests passed! ✓")
