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


def _find_allocation_by_name(allocations, name):
    """Helper function to find an allocation by variable name"""
    return next((a for a in allocations if a.variable_name == name), None)


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
    hru_alloc = _find_allocation_by_name(allocations, "hru")
    assert hru_alloc is not None
    assert len(hru_alloc.allocate_lines) == 2  # Allocated twice
    assert len(hru_alloc.deallocate_lines) == 1  # Deallocated once

    # Find res allocation
    res_alloc = _find_allocation_by_name(allocations, "res")
    assert res_alloc is not None
    assert len(res_alloc.allocate_lines) == 1
    assert len(res_alloc.deallocate_lines) == 1

    # temp should not be tracked (never allocated/deallocated)
    temp_alloc = _find_allocation_by_name(allocations, "temp")
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
    arr_alloc = _find_allocation_by_name(allocations, "arr")
    assert arr_alloc is not None
    assert len(arr_alloc.allocate_lines) == 2  # Allocated in both branches
    assert len(arr_alloc.deallocate_lines) == 1


def test_return_statement_detection():
    """Test that RETURN statements create KEYWORD_EXIT nodes that connect to exit block"""
    source = """
subroutine test_return(x)
    integer, intent(in) :: x

    if (x < 0) then
        return
    end if

    print *, "x is non-negative"
end subroutine test_return
"""
    cfg = parse_control_flow(source, "test_return", "subroutine")

    assert cfg is not None

    # RETURN statements should create KEYWORD_EXIT blocks
    return_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_EXIT
    ]
    assert (
        len(return_keyword_blocks) == 1
    ), "Should have one KEYWORD_EXIT block for RETURN"

    # The RETURN keyword node should connect directly to the exit block
    return_node = return_keyword_blocks[0]
    assert (
        cfg.exit_block_id in return_node.successors
    ), "RETURN node should connect to exit"

    # Find the THEN block (which contains the return statement)
    then_blocks = [b for b in cfg.blocks.values() if b.label == "THEN"]
    assert len(then_blocks) == 1

    # The THEN block should connect to the RETURN keyword node
    then_block = then_blocks[0]
    assert (
        return_node.id in then_block.successors
    ), "THEN block should connect to RETURN node"


def test_multiple_return_statements():
    """Test multiple RETURN statements create KEYWORD_EXIT nodes that connect to exit block"""
    source = """
subroutine test_multiple_returns(x, y)
    integer, intent(in) :: x, y
    
    if (x < 0) then
        return
    end if
    
    if (y < 0) then
        return
    end if
    
    print *, "Both positive"
end subroutine test_multiple_returns
"""
    cfg = parse_control_flow(source, "test_multiple_returns", "subroutine")

    assert cfg is not None

    # Should have KEYWORD_EXIT blocks for each RETURN
    return_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_EXIT
    ]
    assert (
        len(return_keyword_blocks) == 2
    ), "Should have two KEYWORD_EXIT blocks for two RETURNs"

    # All RETURN keyword nodes should connect to exit
    for return_node in return_keyword_blocks:
        assert (
            cfg.exit_block_id in return_node.successors
        ), "RETURN node should connect to exit"


def test_no_return_statement():
    """Test procedure without RETURN statement - should have no return blocks"""
    source = """
subroutine test_no_return(x)
    integer, intent(in) :: x
    
    print *, x
end subroutine test_no_return
"""
    cfg = parse_control_flow(source, "test_no_return", "subroutine")

    assert cfg is not None

    # Should have no return blocks
    return_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.RETURN]
    assert len(return_blocks) == 0


def test_return_in_nested_blocks():
    """Test RETURN statement in nested control structures creates KEYWORD_EXIT node"""
    source = """
subroutine test_nested_return(x, y)
    integer, intent(in) :: x, y

    if (x > 0) then
        if (y > 0) then
            return
        end if
    end if

    print *, "Completed"
end subroutine test_nested_return
"""
    cfg = parse_control_flow(source, "test_nested_return", "subroutine")

    assert cfg is not None

    # Should have a KEYWORD_EXIT block for RETURN
    return_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_EXIT
    ]
    assert (
        len(return_keyword_blocks) == 1
    ), "Should have one KEYWORD_EXIT block for RETURN"

    # The RETURN keyword node should connect to exit
    return_node = return_keyword_blocks[0]
    assert (
        cfg.exit_block_id in return_node.successors
    ), "RETURN node should connect to exit"


def test_return_in_logic_blocks():
    """Test that RETURN statements appear in logic blocks"""
    source = """
subroutine test_return_logic(x)
    integer, intent(in) :: x
    
    if (x < 0) then
        return
    end if
    
    print *, "x is non-negative"
end subroutine test_return_logic
"""
    result = extract_logic_blocks(source, "test_return_logic", "subroutine")

    assert result is not None
    blocks, _ = result

    # Should have an if block and a statements block
    assert len(blocks) >= 1

    # Find the if block
    if_block = None
    for block in blocks:
        if block.block_type == "if":
            if_block = block
            break

    assert if_block is not None
    # The if block should contain the return statement
    assert "return" in if_block.statements


def test_use_statement_detection():
    """Test that USE statements are skipped in CFG (per requirement #2)"""
    source = """
subroutine test_use()
    use some_module
    use another_module, only: some_function
    implicit none
    integer :: x

    x = 1
    print *, x
end subroutine test_use
"""
    cfg = parse_control_flow(source, "test_use", "subroutine")

    assert cfg is not None

    # USE statements should not create blocks (they're filtered out)
    use_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.USE]
    assert len(use_blocks) == 0, "USE blocks should not be created"

    # Should only have entry, exit, and statement blocks
    stmt_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.STATEMENT
    ]
    assert len(stmt_blocks) > 0, "Should have statement blocks for executable code"


def test_use_and_regular_statements():
    """Test that USE statements are filtered out, only regular statements remain"""
    source = """
subroutine test_mixed()
    use math_module
    integer :: result

    result = 42
end subroutine test_mixed
"""
    cfg = parse_control_flow(source, "test_mixed", "subroutine")

    assert cfg is not None

    # USE statements should be filtered out (per requirement #2)
    use_blocks = [b for b in cfg.blocks.values() if b.block_type == BlockType.USE]
    assert len(use_blocks) == 0, "USE blocks should not be created"

    # Should have statement blocks for executable code only
    stmt_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.STATEMENT
    ]

    assert len(stmt_blocks) > 0, "Should have statement blocks"

    # Verify that declarations are also filtered out
    for block in stmt_blocks:
        for stmt in block.statements:
            assert not stmt.lower().startswith(
                "use "
            ), "USE statements should be filtered"
            assert not stmt.lower().startswith(
                "integer"
            ), "Declarations should be filtered"


def test_keyword_io_nodes():
    """Test that I/O keywords create KEYWORD_IO nodes"""
    source = """
subroutine test_io(filename)
    character(len=*), intent(in) :: filename
    integer :: i

    open(unit=10, file=filename)
    read(10, *) i
    write(10, *) "Hello"
    close(10)
end subroutine test_io
"""
    cfg = parse_control_flow(source, "test_io", "subroutine")

    assert cfg is not None

    # Should have KEYWORD_IO blocks for OPEN, READ, WRITE, CLOSE
    io_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_IO
    ]
    assert len(io_keyword_blocks) == 4, "Should have 4 KEYWORD_IO blocks"

    # Check that they have line numbers
    for block in io_keyword_blocks:
        assert (
            block.line_number is not None
        ), f"Block {block.label} should have a line number"


def test_keyword_memory_nodes():
    """Test that memory keywords create KEYWORD_MEMORY nodes"""
    source = """
subroutine test_memory(n)
    integer, intent(in) :: n
    integer, allocatable :: arr(:)

    allocate(arr(n))
    deallocate(arr)
end subroutine test_memory
"""
    cfg = parse_control_flow(source, "test_memory", "subroutine")

    assert cfg is not None

    # Should have KEYWORD_MEMORY blocks for ALLOCATE and DEALLOCATE
    memory_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_MEMORY
    ]
    assert len(memory_keyword_blocks) == 2, "Should have 2 KEYWORD_MEMORY blocks"

    # Check labels
    labels = [b.label for b in memory_keyword_blocks]
    assert any("ALLOCATE" in label for label in labels), "Should have ALLOCATE node"
    assert any("DEALLOCATE" in label for label in labels), "Should have DEALLOCATE node"


def test_keyword_call_nodes():
    """Test that CALL keywords create KEYWORD_CALL nodes"""
    source = """
subroutine test_call()
    call some_procedure()
    call another_procedure()
end subroutine test_call
"""
    cfg = parse_control_flow(source, "test_call", "subroutine")

    assert cfg is not None

    # Should have KEYWORD_CALL blocks for both CALLs
    call_keyword_blocks = [
        b for b in cfg.blocks.values() if b.block_type == BlockType.KEYWORD_CALL
    ]
    assert len(call_keyword_blocks) == 2, "Should have 2 KEYWORD_CALL blocks"


def test_keyword_nodes_in_sequence():
    """Test that multiple keyword nodes are created in sequence"""
    source = """
subroutine test_sequence(n)
    integer, intent(in) :: n
    integer, allocatable :: arr(:)

    allocate(arr(n))
    call initialize(arr)
    read(10, *) arr
    write(20, *) arr
    deallocate(arr)
end subroutine test_sequence
"""
    cfg = parse_control_flow(source, "test_sequence", "subroutine")

    assert cfg is not None

    # Should have 5 keyword blocks total
    keyword_blocks = [
        b
        for b in cfg.blocks.values()
        if b.block_type
        in [BlockType.KEYWORD_IO, BlockType.KEYWORD_MEMORY, BlockType.KEYWORD_CALL]
    ]
    assert len(keyword_blocks) == 5, "Should have 5 keyword blocks"

    # Verify they are connected in sequence
    entry_block = cfg.blocks[cfg.entry_block_id]

    # Find the first keyword block (should be ALLOCATE)
    first_keyword = None
    for succ_id in entry_block.successors:
        block = cfg.blocks[succ_id]
        if block.block_type == BlockType.KEYWORD_MEMORY and "ALLOCATE" in block.label:
            first_keyword = block
            break

    assert first_keyword is not None, "Should have ALLOCATE as first keyword"


def test_keyword_nodes_with_line_numbers():
    """Test that keyword nodes include line numbers in their labels"""
    source = """
subroutine test_line_numbers()
    integer :: x
    
    read(10, *) x
    write(20, *) x
end subroutine test_line_numbers
"""
    cfg = parse_control_flow(source, "test_line_numbers", "subroutine")

    assert cfg is not None

    # All keyword blocks should have line numbers in their labels
    keyword_blocks = [
        b
        for b in cfg.blocks.values()
        if b.block_type
        in [
            BlockType.KEYWORD_IO,
            BlockType.KEYWORD_MEMORY,
            BlockType.KEYWORD_CALL,
            BlockType.KEYWORD_EXIT,
        ]
    ]

    for block in keyword_blocks:
        assert " (L" in block.label, f"Block {block.label} should have line number"
        assert (
            block.line_number is not None
        ), f"Block {block.label} should have line_number field set"


def test_entry_block_with_arguments():
    """Test that entry block shows procedure name with arguments"""
    source = """
subroutine test_args(x, y, z)
    integer, intent(in) :: x, y
    integer, intent(out) :: z
    
    z = x + y
end subroutine test_args
"""
    cfg = parse_control_flow(source, "test_args", "subroutine")

    assert cfg is not None
    assert cfg.entry_block_id is not None

    entry_block = cfg.blocks[cfg.entry_block_id]
    assert entry_block.block_type == BlockType.ENTRY
    assert entry_block.label == "test_args(x, y, z)"


def test_entry_block_no_arguments():
    """Test that entry block shows procedure name with empty parentheses for no args"""
    source = """
function get_value()
    integer :: get_value
    
    get_value = 42
end function get_value
"""
    cfg = parse_control_flow(source, "get_value", "function")

    assert cfg is not None
    assert cfg.entry_block_id is not None

    entry_block = cfg.blocks[cfg.entry_block_id]
    assert entry_block.block_type == BlockType.ENTRY
    assert entry_block.label == "get_value()"


def test_exit_block_label():
    """Test that exit block is labeled 'Return' instead of 'Exit'"""
    source = """
subroutine test_exit()
    print *, "Hello"
end subroutine test_exit
"""
    cfg = parse_control_flow(source, "test_exit", "subroutine")

    assert cfg is not None
    assert cfg.exit_block_id is not None

    exit_block = cfg.blocks[cfg.exit_block_id]
    assert exit_block.block_type == BlockType.EXIT
    assert exit_block.label == "Return"
