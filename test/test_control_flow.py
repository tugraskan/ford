"""Test control flow graph generation"""

import pytest
from ford.control_flow import (
    parse_control_flow,
    FortranControlFlowParser,
    BlockType,
    extract_logic_blocks,
)


def test_simple_if_then_else():
    """Test parsing of simple IF-THEN-ELSE statement"""
    source = """
subroutine test_if(x, result)
    integer, intent(in) :: x
    integer, intent(out) :: result
    
    if (x > 0) then
        result = 1
    else
        result = -1
    end if
end subroutine test_if
"""
    cfg = parse_control_flow(source, "test_if", "subroutine")

    assert cfg is not None
    assert len(cfg.blocks) > 0
    assert cfg.entry_block_id is not None
    assert cfg.exit_block_id is not None

    # Should have entry, exit, condition, then block, else block, merge block
    assert len(cfg.blocks) >= 6

    # Find the IF condition block
    if_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.IF_CONDITION
    ]
    assert len(if_blocks) > 0

    # IF condition should have 2 successors (true and false branches)
    if_block = if_blocks[0]
    assert len(if_block.successors) == 2


def test_do_loop():
    """Test parsing of DO loop"""
    source = """
subroutine test_loop(n, sum)
    integer, intent(in) :: n
    integer, intent(out) :: sum
    integer :: i
    
    sum = 0
    do i = 1, n
        sum = sum + i
    end do
end subroutine test_loop
"""
    cfg = parse_control_flow(source, "test_loop", "subroutine")

    assert cfg is not None

    # Find DO loop blocks
    do_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.DO_LOOP]
    assert len(do_blocks) > 0

    # DO loop should have 2 successors (loop body and after loop)
    do_block = do_blocks[0]
    assert len(do_block.successors) == 2


def test_select_case():
    """Test parsing of SELECT CASE statement"""
    source = """
subroutine test_select(n, result)
    integer, intent(in) :: n
    integer, intent(out) :: result
    
    select case (n)
        case (1)
            result = 10
        case (2)
            result = 20
        case default
            result = 0
    end select
end subroutine test_select
"""
    cfg = parse_control_flow(source, "test_select", "subroutine")

    assert cfg is not None

    # Find SELECT CASE block
    select_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.SELECT_CASE
    ]
    assert len(select_blocks) > 0

    # SELECT should have multiple successors (one for each case)
    select_block = select_blocks[0]
    assert len(select_block.successors) >= 3  # case 1, case 2, case default

    # Find CASE blocks
    case_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.CASE]
    assert len(case_blocks) >= 3


def test_nested_if():
    """Test parsing of nested IF statements"""
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
    cfg = parse_control_flow(source, "test_nested_if", "subroutine")

    assert cfg is not None

    # Should have two IF condition blocks (outer and inner)
    if_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.IF_CONDITION
    ]
    assert len(if_blocks) >= 2


def test_if_without_else():
    """Test parsing of IF without ELSE"""
    source = """
subroutine test_if_no_else(x, result)
    integer, intent(in) :: x
    integer, intent(out) :: result
    
    result = 0
    if (x > 0) then
        result = 1
    end if
end subroutine test_if_no_else
"""
    cfg = parse_control_flow(source, "test_if_no_else", "subroutine")

    assert cfg is not None

    # Find the IF condition block
    if_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.IF_CONDITION
    ]
    assert len(if_blocks) > 0

    # IF condition should have 2 successors even without ELSE (true branch and merge)
    if_block = if_blocks[0]
    assert len(if_block.successors) == 2


def test_function_parsing():
    """Test parsing of function (not just subroutine)"""
    source = """
function calculate_sum(n) result(sum)
    integer, intent(in) :: n
    integer :: sum
    integer :: i
    
    sum = 0
    do i = 1, n
        sum = sum + i
    end do
end function calculate_sum
"""
    cfg = parse_control_flow(source, "calculate_sum", "function")

    assert cfg is not None
    assert cfg.procedure_type == "function"
    assert cfg.procedure_name == "calculate_sum"

    # Should have DO loop
    do_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.DO_LOOP]
    assert len(do_blocks) > 0


def test_empty_procedure():
    """Test parsing of empty procedure"""
    source = """
subroutine empty_sub()
    implicit none
end subroutine empty_sub
"""
    cfg = parse_control_flow(source, "empty_sub", "subroutine")

    assert cfg is not None
    # Should at least have entry and exit blocks
    assert len(cfg.blocks) >= 2
    assert cfg.entry_block_id is not None
    assert cfg.exit_block_id is not None


def test_complex_control_flow():
    """Test a more complex control flow with multiple structures"""
    source = """
subroutine complex_flow(n, x, result)
    integer, intent(in) :: n
    real, intent(in) :: x
    integer, intent(out) :: result
    integer :: i
    
    result = 0
    
    if (n > 0) then
        do i = 1, n
            result = result + i
        end do
    else if (n < 0) then
        result = -1
    else
        result = 0
    end if
    
    select case (result)
        case (0)
            result = 1
        case (1:10)
            result = result * 2
        case default
            result = 100
    end select
end subroutine complex_flow
"""
    cfg = parse_control_flow(source, "complex_flow", "subroutine")

    assert cfg is not None

    # Should have IF, DO, and SELECT CASE blocks
    if_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.IF_CONDITION
    ]
    do_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.DO_LOOP]
    select_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.SELECT_CASE
    ]

    assert len(if_blocks) >= 1  # At least the outer IF
    assert len(do_blocks) >= 1
    assert len(select_blocks) >= 1


def test_logic_blocks_exclude_use_statements():
    """Test that logic blocks exclude USE statements"""
    source = """
subroutine test_use
    use some_module
    use another_module, only: func1, func2
    implicit none
    integer :: x
    
    x = 5
end subroutine test_use
"""
    result = extract_logic_blocks(source, "test_use", "subroutine")

    assert result is not None
    blocks, allocations = result
    # Should have one statements block with only executable statement
    assert len(blocks) == 1
    assert blocks[0].block_type == "statements"
    assert len(blocks[0].statements) == 1
    assert "x = 5" in blocks[0].statements[0]

    # Make sure USE statements are not included
    for block in blocks:
        for stmt in block.statements:
            assert not stmt.strip().lower().startswith("use ")


def test_logic_blocks_exclude_implicit():
    """Test that logic blocks exclude IMPLICIT statements"""
    source = """
subroutine test_implicit
    implicit none
    integer :: x
    
    x = 10
    write(*,*) x
end subroutine test_implicit
"""
    result = extract_logic_blocks(source, "test_implicit", "subroutine")

    assert result is not None
    blocks, allocations = result
    assert len(blocks) == 1
    assert blocks[0].block_type == "statements"

    # Make sure IMPLICIT statements are not included
    for block in blocks:
        for stmt in block.statements:
            assert not stmt.strip().lower().startswith("implicit ")


def test_logic_blocks_exclude_declarations():
    """Test that logic blocks exclude variable declarations"""
    source = """
subroutine test_declarations
    implicit none
    integer :: x, y
    real :: z
    double precision :: a
    complex :: c
    logical :: flag
    character(len=20) :: name
    type(my_type) :: obj
    
    x = 5
    y = 10
    z = 3.14
end subroutine test_declarations
"""
    result = extract_logic_blocks(source, "test_declarations", "subroutine")

    assert result is not None
    blocks, allocations = result
    # Should have one statements block with only executable statements
    assert len(blocks) == 1
    assert blocks[0].block_type == "statements"
    assert len(blocks[0].statements) == 3

    # Check that only assignments are included, not declarations
    for stmt in blocks[0].statements:
        assert "=" in stmt  # All should be assignments
        assert "::" not in stmt  # None should be declarations


def test_logic_blocks_with_control_flow_exclude_declarations():
    """Test that logic blocks with control flow exclude declarations"""
    source = """
subroutine test_control_flow
    use some_module
    implicit none
    integer :: x, y
    real :: result
    
    x = 5
    if (x > 3) then
        y = 10
        result = x + y
    else
        result = 0
    end if
end subroutine test_control_flow
"""
    result = extract_logic_blocks(source, "test_control_flow", "subroutine")

    assert result is not None
    blocks, allocations = result
    # Should have a statements block and an if block
    assert len(blocks) >= 2

    # First block should be statements with only executable code
    stmt_blocks = [b for b in blocks if b.block_type == "statements"]
    assert len(stmt_blocks) >= 1

    # Check no declarations in statements
    for block in stmt_blocks:
        for stmt in block.statements:
            assert not stmt.strip().lower().startswith("use ")
            assert not stmt.strip().lower().startswith("implicit ")
            assert "::" not in stmt or "=" in stmt  # Either no :: or it's an assignment

    # Should have an if block
    if_blocks = [b for b in blocks if b.block_type == "if"]
    assert len(if_blocks) >= 1


def test_logic_blocks_exclude_class_and_procedure_declarations():
    """Test that logic blocks exclude CLASS and PROCEDURE pointer declarations"""
    source = """
subroutine test_class_procedure
    use some_module
    implicit none
    class(base_type), pointer :: obj
    procedure(interface_name), pointer :: proc_ptr
    integer :: x
    
    x = 10
    call obj%method()
end subroutine test_class_procedure
"""
    result = extract_logic_blocks(source, "test_class_procedure", "subroutine")

    assert result is not None
    blocks, allocations = result
    # Should have one statements block with only executable statements
    assert len(blocks) == 1
    assert blocks[0].block_type == "statements"
    assert len(blocks[0].statements) == 2

    # Verify the actual statements
    assert "x = 10" in blocks[0].statements[0]
    assert "call obj%method()" in blocks[0].statements[1]

    # Check that no class or procedure declarations are present
    for stmt in blocks[0].statements:
        # If it contains :: it should not be a class or procedure declaration
        if "::" in stmt:
            assert not (stmt.strip().lower().startswith("class"))
            assert not (stmt.strip().lower().startswith("procedure"))


def test_logic_blocks_empty_after_filtering():
    """Test that procedures with only declarations produce no logic blocks"""
    source = """
subroutine test_empty_logic
    use some_module
    implicit none
    integer :: x, y
    real :: z
end subroutine test_empty_logic
"""
    result = extract_logic_blocks(source, "test_empty_logic", "subroutine")

    assert result is not None
    blocks, allocations = result
    # Should have no blocks since all statements are filtered out
    assert len(blocks) == 0


def test_case_blocks_have_line_ranges():
    """Test that CASE blocks have start_line and end_line set"""
    source = """
subroutine test_select(n, result)
    integer, intent(in) :: n
    integer, intent(out) :: result
    
    select case (n)
        case (1)
            result = 10
            result = result + 1
        case (2)
            result = 20
        case default
            result = 0
    end select
end subroutine test_select
"""
    result = extract_logic_blocks(source, "test_select", "subroutine")

    assert result is not None
    blocks, allocations = result
    assert len(blocks) > 0

    # Find SELECT block
    select_blocks = [b for b in blocks if b.block_type == "select"]
    assert len(select_blocks) == 1

    select_block = select_blocks[0]

    # SELECT block should have start_line and end_line
    assert select_block.start_line is not None
    assert select_block.end_line is not None

    # Each CASE should have start_line and end_line
    case_blocks = [
        child for child in select_block.children if child.block_type == "case"
    ]
    assert len(case_blocks) == 3

    for case_block in case_blocks:
        assert (
            case_block.start_line is not None
        ), f"CASE block missing start_line: {case_block.condition}"
        assert (
            case_block.end_line is not None
        ), f"CASE block missing end_line: {case_block.condition}"
        # end_line should be >= start_line
        assert case_block.end_line >= case_block.start_line


def test_allocation_tracking():
    """Test that allocate and deallocate statements are tracked"""
    source = """
subroutine test_allocations
    implicit none
    integer, allocatable :: hru(:), res(:)
    real, allocatable :: temp(:)
    
    allocate(hru(10))
    allocate(res(5))
    allocate(hru(20))
    
    deallocate(hru)
    deallocate(res)
end subroutine test_allocations
"""
    result = extract_logic_blocks(source, "test_allocations", "subroutine")

    assert result is not None
    blocks, allocations = result
    
    # Should have tracked allocations
    assert len(allocations) > 0
    
    # Find hru allocation
    hru_alloc = next((a for a in allocations if a.variable_name == "hru"), None)
    assert hru_alloc is not None
    assert len(hru_alloc.allocate_lines) == 2  # Allocated twice
    assert len(hru_alloc.deallocate_lines) == 1  # Deallocated once
    
    # Find res allocation
    res_alloc = next((a for a in allocations if a.variable_name == "res"), None)
    assert res_alloc is not None
    assert len(res_alloc.allocate_lines) == 1
    assert len(res_alloc.deallocate_lines) == 1
    
    # temp should not be tracked (never allocated/deallocated)
    temp_alloc = next((a for a in allocations if a.variable_name == "temp"), None)
    assert temp_alloc is None


def test_allocation_tracking_with_control_flow():
    """Test that allocations inside control flow are tracked"""
    source = """
subroutine test_alloc_control
    implicit none
    integer, allocatable :: arr(:)
    integer :: n
    
    n = 10
    if (n > 5) then
        allocate(arr(n))
    else
        allocate(arr(1))
    end if
    
    deallocate(arr)
end subroutine test_alloc_control
"""
    result = extract_logic_blocks(source, "test_alloc_control", "subroutine")

    assert result is not None
    blocks, allocations = result
    
    # Should have tracked allocation of arr
    assert len(allocations) > 0
    arr_alloc = next((a for a in allocations if a.variable_name == "arr"), None)
    assert arr_alloc is not None
    assert len(arr_alloc.allocate_lines) == 2  # Allocated in both branches
    assert len(arr_alloc.deallocate_lines) == 1
