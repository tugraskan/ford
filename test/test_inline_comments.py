"""Test for inline comment handling in control flow structures"""

import pytest
from ford.control_flow import extract_logic_blocks, parse_control_flow


def test_do_loop_with_inline_comment():
    """Test that DO loops with inline comments in END DO are correctly matched"""
    source = """
subroutine test_inline_comment(n)
    integer, intent(in) :: n
    integer :: i
    
    do i = 1, n  ! Loop through data
        print *, i
    end do  ! End of data loop
end subroutine test_inline_comment
"""
    result = extract_logic_blocks(source, "test_inline_comment", "subroutine")
    
    assert result is not None
    blocks, allocations = result
    
    # Find DO block
    do_blocks = [b for b in blocks if b.block_type == "do"]
    assert len(do_blocks) == 1
    
    do_block = do_blocks[0]
    # Verify end_line is set (this is the key fix - END DO with inline comment is now matched)
    assert do_block.end_line is not None
    assert do_block.end_line > do_block.start_line


def test_if_with_inline_comment():
    """Test that IF blocks with inline comments in END IF are correctly matched"""
    source = """
subroutine test_if_inline(x)
    integer, intent(in) :: x
    
    if (x > 0) then  ! Check positive
        print *, "positive"
    end if  ! End of positive check
end subroutine test_if_inline
"""
    result = extract_logic_blocks(source, "test_if_inline", "subroutine")
    
    assert result is not None
    blocks, allocations = result
    
    # Find IF block
    if_blocks = [b for b in blocks if b.block_type == "if"]
    assert len(if_blocks) == 1
    
    if_block = if_blocks[0]
    # Verify end_line is set (this is the key fix - END IF with inline comment is now matched)
    assert if_block.end_line is not None
    assert if_block.end_line > if_block.start_line


def test_select_with_inline_comment():
    """Test that SELECT CASE blocks with inline comments are correctly matched"""
    source = """
subroutine test_select_inline(mode)
    integer, intent(in) :: mode
    
    select case (mode)  ! Check mode
    case (1)
        print *, "mode 1"
    case default
        print *, "other"
    end select  ! End of mode check
end subroutine test_select_inline
"""
    result = extract_logic_blocks(source, "test_select_inline", "subroutine")
    
    assert result is not None
    blocks, allocations = result
    
    # Find SELECT block
    select_blocks = [b for b in blocks if b.block_type == "select"]
    assert len(select_blocks) == 1
    
    select_block = select_blocks[0]
    # Verify end_line is set (this is the key fix - END SELECT with inline comment is now matched)
    assert select_block.end_line is not None
    assert select_block.end_line > select_block.start_line


def test_nested_structures_with_inline_comments():
    """Test that nested structures with inline comments are correctly matched"""
    source = """
subroutine test_nested_inline(n, mode)
    integer, intent(in) :: n, mode
    integer :: i
    
    if (n > 0) then  ! Check n
        do i = 1, n  ! Loop
            select case (mode)  ! Check mode
            case (1)
                print *, i
            end select  ! End mode check
        end do  ! End loop
    end if  ! End n check
end subroutine test_nested_inline
"""
    result = extract_logic_blocks(source, "test_nested_inline", "subroutine")
    
    assert result is not None
    blocks, allocations = result
    
    # Find IF block
    if_blocks = [b for b in blocks if b.block_type == "if"]
    assert len(if_blocks) == 1
    if_block = if_blocks[0]
    assert if_block.end_line is not None
    assert if_block.end_line > if_block.start_line
    
    # Find DO block (child of IF)
    do_blocks = [c for c in if_block.children if c.block_type == "do"]
    assert len(do_blocks) == 1
    do_block = do_blocks[0]
    assert do_block.end_line is not None
    assert do_block.end_line > do_block.start_line
    
    # Find SELECT block (child of DO)
    select_blocks = [c for c in do_block.children if c.block_type == "select"]
    assert len(select_blocks) == 1
    select_block = select_blocks[0]
    assert select_block.end_line is not None
    assert select_block.end_line > select_block.start_line
    
    # The important check: end_do comes after end_select which comes after case content
    assert select_block.end_line < do_block.end_line < if_block.end_line


def test_control_flow_graph_with_inline_comments():
    """Test that control flow graph correctly handles inline comments"""
    source = """
subroutine test_cfg_inline(n)
    integer, intent(in) :: n
    integer :: i
    
    do i = 1, n  ! Loop through data
        print *, i
    end do  ! End of loop
end subroutine test_cfg_inline
"""
    cfg = parse_control_flow(source, "test_cfg_inline", "subroutine")
    
    assert cfg is not None
    
    # Find DO loop blocks
    from ford.control_flow import BlockType
    do_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.DO_LOOP]
    assert len(do_blocks) == 1
    
    # Verify the DO block has a line number
    do_block = do_blocks[0]
    assert do_block.line_number is not None
    
    # Find loop body and after-loop blocks to verify graph structure
    assert len(do_block.successors) == 2  # Loop body and exit
