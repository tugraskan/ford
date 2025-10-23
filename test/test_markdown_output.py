import shutil
import sys
import pathlib
import json
import pytest

import ford

from conftest import chdir


@pytest.fixture(scope="module")
def markdown_example_project(tmp_path_factory):
    """Build the example project with markdown output"""
    this_dir = pathlib.Path(__file__).parent
    tmp_path = tmp_path_factory.getbasetemp() / "example_markdown"
    shutil.copytree(this_dir / "../example", tmp_path)

    # Modify the project file to use markdown output
    fpm_toml = tmp_path / "fpm.toml"
    content = fpm_toml.read_text()
    content = content.replace('output_dir = "./doc"', 'output_dir = "./doc"\noutput_format = "markdown"')
    fpm_toml.write_text(content)

    with pytest.MonkeyPatch.context() as m, chdir(tmp_path):
        m.setattr(sys, "argv", ["ford", "example-project-file.md"])
        ford.run()

    doc_path = tmp_path / "doc"
    return doc_path


@pytest.fixture(scope="module")
def gitbook_example_project(tmp_path_factory):
    """Build the example project with gitbook output"""
    this_dir = pathlib.Path(__file__).parent
    tmp_path = tmp_path_factory.getbasetemp() / "example_gitbook"
    shutil.copytree(this_dir / "../example", tmp_path)

    # Modify the project file to use gitbook output
    fpm_toml = tmp_path / "fpm.toml"
    content = fpm_toml.read_text()
    content = content.replace('output_dir = "./doc"', 'output_dir = "./doc"\noutput_format = "gitbook"')
    fpm_toml.write_text(content)

    with pytest.MonkeyPatch.context() as m, chdir(tmp_path):
        m.setattr(sys, "argv", ["ford", "example-project-file.md"])
        ford.run()

    doc_path = tmp_path / "doc"
    return doc_path


def test_markdown_index_created(markdown_example_project):
    """Test that the main index.md file is created"""
    doc_path = markdown_example_project
    index = doc_path / "index.md"
    assert index.exists()
    content = index.read_text()
    assert "# Example Project" in content
    assert "## Documentation" in content


def test_markdown_modules_created(markdown_example_project):
    """Test that module documentation files are created"""
    doc_path = markdown_example_project
    modules_dir = doc_path / "modules"
    assert modules_dir.exists()
    assert (modules_dir / "index.md").exists()
    
    # Check that individual module files exist
    assert (modules_dir / "test_module.md").exists()
    assert (modules_dir / "ford_example_type_mod.md").exists()
    
    # Check content of a module file
    module_content = (modules_dir / "test_module.md").read_text()
    assert "# Module: test_module" in module_content


def test_markdown_procedures_created(markdown_example_project):
    """Test that procedure documentation files are created"""
    doc_path = markdown_example_project
    procs_dir = doc_path / "procedures"
    assert procs_dir.exists()
    assert (procs_dir / "index.md").exists()
    
    # Check that individual procedure files exist
    assert (procs_dir / "increment.md").exists()
    assert (procs_dir / "decrement.md").exists()


def test_markdown_types_created(markdown_example_project):
    """Test that type documentation files are created"""
    doc_path = markdown_example_project
    types_dir = doc_path / "types"
    assert types_dir.exists()
    assert (types_dir / "index.md").exists()
    
    # Check that individual type files exist
    assert (types_dir / "foo.md").exists()
    assert (types_dir / "example_type.md").exists()
    
    # Check content of a type file
    type_content = (types_dir / "example_type.md").read_text()
    assert "# Type: example_type" in type_content


def test_markdown_programs_created(markdown_example_project):
    """Test that program documentation files are created"""
    doc_path = markdown_example_project
    progs_dir = doc_path / "programs"
    assert progs_dir.exists()
    assert (progs_dir / "index.md").exists()
    
    # Check that individual program files exist
    assert (progs_dir / "ford_test_program.md").exists()


def test_markdown_custom_pages_created(markdown_example_project):
    """Test that custom user pages are created"""
    doc_path = markdown_example_project
    pages_dir = doc_path / "pages"
    assert pages_dir.exists()
    
    # Check that custom pages exist
    assert (pages_dir / "first_page.md").exists()
    assert (pages_dir / "second_page.md").exists()


def test_gitbook_readme_created(gitbook_example_project):
    """Test that GitBook README.md is created"""
    doc_path = gitbook_example_project
    readme = doc_path / "README.md"
    assert readme.exists()
    content = readme.read_text()
    assert "# Example Project" in content


def test_gitbook_summary_created(gitbook_example_project):
    """Test that GitBook SUMMARY.md is created"""
    doc_path = gitbook_example_project
    summary = doc_path / "SUMMARY.md"
    assert summary.exists()
    content = summary.read_text()
    assert "# Summary" in content
    assert "* [Introduction](README.md)" in content
    assert "## Modules" in content
    assert "## Procedures" in content
    assert "## Types" in content


def test_gitbook_book_json_created(gitbook_example_project):
    """Test that GitBook book.json is created"""
    doc_path = gitbook_example_project
    book_json = doc_path / "book.json"
    assert book_json.exists()
    
    with open(book_json) as f:
        book_data = json.load(f)
    
    assert book_data["title"] == "Example Project"
    assert "author" in book_data
    assert book_data["structure"]["readme"] == "README.md"
    assert book_data["structure"]["summary"] == "SUMMARY.md"


def test_markdown_module_content_structure(markdown_example_project):
    """Test the structure of a module markdown file"""
    doc_path = markdown_example_project
    module_file = doc_path / "modules" / "test_module.md"
    content = module_file.read_text()
    
    # Check for expected sections
    assert "# Module:" in content
    assert "## Procedures" in content or "## Types" in content or "## Variables" in content


def test_markdown_procedure_content_structure(markdown_example_project):
    """Test the structure of a procedure markdown file"""
    doc_path = markdown_example_project
    proc_file = doc_path / "procedures" / "increment.md"
    content = proc_file.read_text()
    
    # Check for expected sections
    assert "# " in content  # Has a heading
    assert "increment" in content.lower()


def test_markdown_type_content_structure(markdown_example_project):
    """Test the structure of a type markdown file"""
    doc_path = markdown_example_project
    type_file = doc_path / "types" / "example_type.md"
    content = type_file.read_text()
    
    # Check for expected sections
    assert "# Type:" in content
    assert "example_type" in content


def test_output_format_validation():
    """Test that invalid output_format raises an error"""
    from ford.settings import ProjectSettings
    
    with pytest.raises(ValueError, match="Invalid output_format"):
        ProjectSettings(output_format="invalid")


def test_valid_output_formats():
    """Test that valid output formats are accepted"""
    from ford.settings import ProjectSettings
    
    # These should not raise errors
    ProjectSettings(output_format="html")
    ProjectSettings(output_format="markdown")
    ProjectSettings(output_format="gitbook")
    ProjectSettings(output_format="HTML")  # Case insensitive
    ProjectSettings(output_format="Markdown")
