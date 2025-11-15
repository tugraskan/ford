"""Test control flow graph collapse functionality"""
import pytest
from ford.control_flow import parse_control_flow, BlockType
from ford.graphs import create_control_flow_graph_svg


def test_collapse_indicators_added_to_if_blocks():
    """Test that collapse indicators are added to IF blocks"""
    source = """
    subroutine test_if(n)
        integer, intent(in) :: n
        
        if (n > 0) then
            write(*,*) 'Positive'
        end if
    end subroutine test_if
    """
    
    cfg = parse_control_flow(source, 'test_if', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_if')
    
    # Check that the SVG contains collapse indicators
    assert 'data-collapsible="true"' in svg
    assert 'data-block-type="if_condition"' in svg
    assert 'class="collapse-indicator"' in svg
    assert 'class="collapse-icon"' in svg
    assert 'cfg-collapsible' in svg


def test_collapse_indicators_added_to_do_loops():
    """Test that collapse indicators are added to DO loops"""
    source = """
    subroutine test_do(n)
        integer, intent(in) :: n
        integer :: i
        
        do i = 1, n
            write(*,*) i
        end do
    end subroutine test_do
    """
    
    cfg = parse_control_flow(source, 'test_do', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_do')
    
    # Check that the SVG contains collapse indicators
    assert 'data-collapsible="true"' in svg
    assert 'data-block-type="do_loop"' in svg
    assert 'class="collapse-indicator"' in svg


def test_collapse_indicators_added_to_select_case():
    """Test that collapse indicators are added to SELECT CASE blocks"""
    source = """
    subroutine test_select(mode)
        character(len=*), intent(in) :: mode
        
        select case (mode)
        case ('a')
            write(*,*) 'Mode A'
        case ('b')
            write(*,*) 'Mode B'
        case default
            write(*,*) 'Unknown'
        end select
    end subroutine test_select
    """
    
    cfg = parse_control_flow(source, 'test_select', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_select')
    
    # Check that the SVG contains collapse indicators
    assert 'data-collapsible="true"' in svg
    assert 'data-block-type="select_case"' in svg
    assert 'class="collapse-indicator"' in svg


def test_multiple_collapsible_nodes():
    """Test that multiple collapsible nodes are created correctly"""
    source = """
    subroutine test_multiple(n, mode)
        integer, intent(in) :: n
        character(len=*), intent(in) :: mode
        integer :: i
        
        if (n > 0) then
            do i = 1, n
                select case (mode)
                case ('fast')
                    write(*,*) 'Fast'
                case default
                    write(*,*) 'Default'
                end select
            end do
        end if
    end subroutine test_multiple
    """
    
    cfg = parse_control_flow(source, 'test_multiple', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_multiple')
    
    # Count collapsible nodes (IF + DO + SELECT)
    import re
    collapsible_count = len(re.findall(r'data-collapsible="true"', svg))
    assert collapsible_count == 3, f"Expected 3 collapsible nodes, found {collapsible_count}"
    
    # Check that all three types are present
    assert 'data-block-type="if_condition"' in svg
    assert 'data-block-type="do_loop"' in svg
    assert 'data-block-type="select_case"' in svg


def test_collapse_icon_initial_state():
    """Test that collapse icons start in expanded state (minus sign)"""
    source = """
    subroutine test_icon(n)
        integer, intent(in) :: n
        
        if (n > 0) then
            write(*,*) 'Positive'
        end if
    end subroutine test_icon
    """
    
    cfg = parse_control_flow(source, 'test_icon', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_icon')
    
    # Check that the minus sign is present (expanded state)
    assert '−' in svg or '&minus;' in svg or '-' in svg


def test_non_collapsible_nodes_unchanged():
    """Test that non-collapsible nodes (ENTRY, EXIT, STATEMENT) are not modified"""
    source = """
    subroutine test_simple()
        write(*,*) 'Simple'
    end subroutine test_simple
    """
    
    cfg = parse_control_flow(source, 'test_simple', 'subroutine')
    svg = create_control_flow_graph_svg(cfg, 'test_simple')
    
    # Should not have any collapsible indicators since there are no control structures
    assert 'data-collapsible="true"' not in svg
    assert 'class="collapse-indicator"' not in svg
