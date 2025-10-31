"""Test nested DO loop control flow formatting"""

import pytest
from ford.control_flow import extract_logic_blocks


def test_nested_do_loops_end_statements():
    """Test that END DO statements are not included in statement lists"""
    source = """
subroutine aqu_pest_output_init
    use aqu_pesticide_module
    implicit none
    integer :: ipest, iaq
    
    do iaq = 1, 10
        do ipest = 1, 5
            baqupst_d = 0.
            baqupst_m = 0.
        end do
        
        do ipest = 1, 5
            aqupst_d = 1.
            baqupst_d = baqupst_d + 1.
        end do
    end do
    
    return
end subroutine aqu_pest_output_init
"""
    blocks = extract_logic_blocks(source, "aqu_pest_output_init", "subroutine")
    
    assert blocks is not None
    assert len(blocks) >= 1
    
    # Find the outer DO loop
    do_blocks = [b for b in blocks if b.block_type == "do"]
    assert len(do_blocks) == 1
    outer_do = do_blocks[0]
    
    # The outer DO should have 2 child DO loops
    child_dos = [c for c in outer_do.children if c.block_type == "do"]
    assert len(child_dos) == 2
    
    # Verify that END DO is NOT in any statements
    for child_do in child_dos:
        for stmt in child_do.statements:
            assert "end do" not in stmt.lower(), f"Found 'end do' in statements: {stmt}"
    
    # Also check outer DO
    for stmt in outer_do.statements:
        assert "end do" not in stmt.lower(), f"Found 'end do' in outer statements: {stmt}"


def test_nested_if_end_statements():
    """Test that END IF statements are not included in statement lists"""
    source = """
subroutine test_nested_if(x, y, result)
    integer, intent(in) :: x, y
    integer, intent(out) :: result
    
    if (x > 0) then
        if (y > 0) then
            result = 1
        else
            result = 2
        end if
    else
        result = -1
    end if
end subroutine test_nested_if
"""
    blocks = extract_logic_blocks(source, "test_nested_if", "subroutine")
    
    assert blocks is not None
    
    # Find all IF/ELSE/ELSEIF blocks
    if_blocks = [b for b in blocks if b.block_type in ["if", "else", "elseif"]]
    assert len(if_blocks) >= 1
    
    # Check all blocks recursively
    def check_no_end_if(block):
        for stmt in block.statements:
            assert "end if" not in stmt.lower(), f"Found 'end if' in statements: {stmt}"
        for child in block.children:
            check_no_end_if(child)
    
    for block in blocks:
        check_no_end_if(block)


def test_do_loop_end_line_tracking():
    """Test that end_line is still correctly set for DO loops"""
    source = """
subroutine test_loop(n)
    integer :: n, i
    
    do i = 1, n
        n = n + 1
    end do
end subroutine test_loop
"""
    blocks = extract_logic_blocks(source, "test_loop", "subroutine")
    
    assert blocks is not None
    do_blocks = [b for b in blocks if b.block_type == "do"]
    assert len(do_blocks) == 1
    
    do_block = do_blocks[0]
    # end_line should be set to the line number of 'end do'
    assert do_block.end_line is not None
    assert do_block.end_line > do_block.start_line


def test_if_end_line_tracking():
    """Test that end_line is still correctly set for IF blocks"""
    source = """
subroutine test_if(x)
    integer :: x
    
    if (x > 0) then
        x = x + 1
    end if
end subroutine test_if
"""
    blocks = extract_logic_blocks(source, "test_if", "subroutine")
    
    assert blocks is not None
    if_blocks = [b for b in blocks if b.block_type == "if"]
    assert len(if_blocks) == 1
    
    if_block = if_blocks[0]
    # end_line should be set to the line number of 'end if'
    assert if_block.end_line is not None
    assert if_block.end_line > if_block.start_line
