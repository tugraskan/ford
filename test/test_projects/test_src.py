"""Test that FORD can successfully process the test_data/src directory."""
import shutil
import sys
import pathlib

import ford
import pytest

from conftest import chdir


@pytest.fixture(scope="module")
def src_project(tmp_path_factory):
    """Generate documentation for the test_data/src directory."""
    this_dir = pathlib.Path(__file__).parent
    tmp_path = tmp_path_factory.getbasetemp() / "src"
    shutil.copytree(this_dir / "../../test_data/src", tmp_path)

    with pytest.MonkeyPatch.context() as m, chdir(tmp_path):
        m.setattr(sys, "argv", ["ford", "doc.md"])
        ford.run()

    doc_path = tmp_path / "doc"
    return doc_path


def test_src_documentation_generated(src_project):
    """Test that documentation was successfully generated for test_data/src."""
    # Check that the main index.html file was created
    assert (src_project / "index.html").exists()
    
    # Check that some expected directories were created
    assert (src_project / "proc").exists()
    assert (src_project / "module").exists()
    assert (src_project / "type").exists()
    
    # Check that the search.html file was created (search is enabled by default)
    # Actually, we disabled search in the doc.md file, so this shouldn't exist
    # But let's just verify the main page exists
    assert (src_project / "lists").exists()
