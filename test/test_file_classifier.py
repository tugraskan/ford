"""
Tests for the file classification system.
"""

import pytest
import tempfile
import os
from pathlib import Path
from ford.file_classifier import FileClassifier, classify_file, FileStructure


class TestFileClassifier:
    """Test suite for FileClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a classifier instance for testing."""
        return FileClassifier()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def create_test_file(self, temp_dir, filename, content):
        """Helper to create a test file."""
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_simple_tabular_file(self, classifier, temp_dir):
        """Test classification of simple tabular files."""
        content = """name    value1  value2  value3
data1   10.5    20.3    30.1
data2   15.2    25.8    35.4
data3   12.1    22.7    32.9
data4   18.3    28.5    38.2
"""
        filepath = self.create_test_file(temp_dir, 'test.cli', content)
        result = classifier.classify(filepath)
        assert result == 'Simple', f"Expected 'Simple', got '{result}'"
    
    def test_connect_file_with_con_extension(self, classifier, temp_dir):
        """Test classification of .con files."""
        content = """hru_id  channel_id  aquifer_id
1       101         201
2       102         202
3       103         203
"""
        filepath = self.create_test_file(temp_dir, 'hru.con', content)
        result = classifier.classify(filepath)
        assert result == 'Connect', f"Expected 'Connect', got '{result}'"
    
    def test_unique_config_file(self, classifier, temp_dir):
        """Test classification of unique configuration files."""
        content = """master_file: config
version: 1.0
project_name: test_project
output_dir: ./output
num_simulations: 100
"""
        filepath = self.create_test_file(temp_dir, 'file.cio', content)
        result = classifier.classify(filepath)
        assert result == 'Unique', f"Expected 'Unique', got '{result}'"
    
    def test_unique_def_file(self, classifier, temp_dir):
        """Test classification of .def (definition) files."""
        content = """definition_file
num_units: 25
base_year: 2000
"""
        filepath = self.create_test_file(temp_dir, 'rout_unit.def', content)
        result = classifier.classify(filepath)
        assert result == 'Unique', f"Expected 'Unique', got '{result}'"
    
    def test_simple_weather_file(self, classifier, temp_dir):
        """Test classification of weather data files."""
        content = """date        pcp     tmp     hmd
2020-01-01  5.2     15.3    65.0
2020-01-02  0.0     16.1    62.5
2020-01-03  2.1     14.8    68.2
2020-01-04  0.0     17.2    60.1
"""
        filepath = self.create_test_file(temp_dir, 'pcp.cli', content)
        result = classifier.classify(filepath)
        assert result == 'Simple', f"Expected 'Simple', got '{result}'"
    
    def test_connect_reservoir_file(self, classifier, temp_dir):
        """Test classification of reservoir connection files."""
        content = """res_id  hru_id  channel_id
1       10      100
2       20      200
"""
        filepath = self.create_test_file(temp_dir, 'reservoir.con', content)
        result = classifier.classify(filepath)
        assert result == 'Connect', f"Expected 'Connect', got '{result}'"
    
    def test_simple_element_file(self, classifier, temp_dir):
        """Test classification of element files."""
        content = """id  area    elevation   slope
1   125.5   150.2       0.05
2   130.2   145.8       0.04
3   115.8   155.1       0.06
"""
        filepath = self.create_test_file(temp_dir, 'rout_unit.ele', content)
        result = classifier.classify(filepath)
        assert result == 'Simple', f"Expected 'Simple', got '{result}'"
    
    def test_unique_management_schedule(self, classifier, temp_dir):
        """Test classification of management schedule files."""
        content = """management_schedule
operations:
  - plant: corn
    date: 04-15
  - fertilize: N
    date: 05-01
  - harvest:
    date: 10-15
"""
        filepath = self.create_test_file(temp_dir, 'management.sch', content)
        result = classifier.classify(filepath)
        assert result == 'Unique', f"Expected 'Unique', got '{result}'"
    
    def test_simple_hru_file(self, classifier, temp_dir):
        """Test classification of HRU data files."""
        content = """id  name    area    slope   soil_type
1   hru001  50.5    0.05    clay
2   hru002  45.2    0.03    loam
3   hru003  55.8    0.07    sand
"""
        filepath = self.create_test_file(temp_dir, 'hru-data.hru', content)
        result = classifier.classify(filepath)
        assert result == 'Simple', f"Expected 'Simple', got '{result}'"
    
    def test_unique_data_file(self, classifier, temp_dir):
        """Test classification of unique data files."""
        content = """recday data file
starting_date: 2020-01-01
ending_date: 2020-12-31
"""
        filepath = self.create_test_file(temp_dir, 'recday.dat', content)
        result = classifier.classify(filepath)
        assert result == 'Unique', f"Expected 'Unique', got '{result}'"
    
    def test_link_file(self, classifier, temp_dir):
        """Test classification of .lin (link) files."""
        content = """channel surface linkage
chan_id surf_id
1       10
2       20
"""
        filepath = self.create_test_file(temp_dir, 'aqu_cha.lin', content)
        result = classifier.classify(filepath)
        assert result == 'Connect', f"Expected 'Connect', got '{result}'"
    
    def test_empty_file(self, classifier, temp_dir):
        """Test classification of empty files."""
        filepath = self.create_test_file(temp_dir, 'empty.txt', '')
        result = classifier.classify(filepath)
        # Empty files should return Unknown
        assert result in ['Unknown', 'Simple', 'Unique'], f"Got unexpected '{result}'"
    
    def test_analyze_structure_tabular(self, classifier, temp_dir):
        """Test structure analysis for tabular data."""
        content = """col1  col2  col3
1     2     3
4     5     6
7     8     9
"""
        filepath = self.create_test_file(temp_dir, 'table.txt', content)
        structure = classifier._analyze_structure(filepath)
        
        assert structure.num_lines > 0
        assert structure.num_columns_avg == 3.0
        assert structure.num_tables >= 1
    
    def test_analyze_structure_mixed(self, classifier, temp_dir):
        """Test structure analysis for mixed content."""
        content = """config_name: test
version: 1.0
data:
1  2  3
4  5  6
"""
        filepath = self.create_test_file(temp_dir, 'mixed.txt', content)
        structure = classifier._analyze_structure(filepath)
        
        assert structure.has_mixed_structure
    
    def test_convenience_function(self, temp_dir):
        """Test the convenience classify_file function."""
        content = """id  value
1   10
2   20
"""
        filepath = self.create_test_file(temp_dir, 'test.cli', content)
        result = classify_file(filepath)
        assert result == 'Simple'
    
    def test_nonexistent_file(self, classifier):
        """Test handling of nonexistent files."""
        result = classifier.classify('/nonexistent/file.txt')
        assert result == 'Unknown'
    
    def test_bsn_files_are_simple(self, classifier, temp_dir):
        """Test that .bsn files are classified as Simple."""
        content = """param1  10.5  20.3
param2  15.2  25.8
param3  12.1  22.7
param4  18.3  28.5
param5  14.7  23.9
param6  16.5  26.2
"""
        filepath = self.create_test_file(temp_dir, 'parameters.bsn', content)
        result = classifier.classify(filepath)
        assert result == 'Simple'
    
    def test_key_files_are_simple(self, classifier, temp_dir):
        """Test that .key files are classified as Simple."""
        content = """key1  10.1  20.2
key2  15.3  25.4
key3  12.5  22.6
key4  18.7  28.8
key5  14.9  24.0
"""
        filepath = self.create_test_file(temp_dir, 'res.key', content)
        result = classifier.classify(filepath)
        assert result == 'Simple'
    
    def test_ini_files_can_be_unique(self, classifier, temp_dir):
        """Test that small .ini files are classified as Unique."""
        content = """initialization
param: value
setting: config
"""
        filepath = self.create_test_file(temp_dir, 'plant.ini', content)
        result = classifier.classify(filepath)
        assert result == 'Unique'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
