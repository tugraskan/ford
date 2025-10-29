#!/usr/bin/env python
"""Test logic block extraction"""

from ford.control_flow import extract_logic_blocks

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

blocks = extract_logic_blocks(source, "test_if", "subroutine")
print(f"Extracted {len(blocks) if blocks else 0} blocks")
if blocks:
    for i, block in enumerate(blocks):
        print(f"Block {i}: type={block.block_type}, condition={block.condition}, level={block.level}")
        print(f"  Statements: {block.statements}")
        print(f"  Children: {len(block.children)}")
