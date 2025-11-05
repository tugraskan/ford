# -*- coding: utf-8 -*-
#
#  control_flow.py
#  This file is part of FORD.
#
#  Copyright 2024
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

"""
Control flow graph generation for Fortran procedures.

This module provides functionality to parse Fortran subroutines and functions,
extract control flow structures (IF, DO, SELECT CASE, etc.), and generate
control flow graphs showing the execution order and conditions.
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class BlockType(Enum):
    """Types of basic blocks in a control flow graph"""

    ENTRY = "entry"
    EXIT = "exit"
    RETURN = "return"
    STATEMENT = "statement"
    IF_CONDITION = "if_condition"
    DO_LOOP = "do_loop"
    SELECT_CASE = "select_case"
    CASE = "case"


@dataclass
class BasicBlock:
    """Represents a basic block in a control flow graph

    A basic block is a sequence of statements with a single entry point
    and a single exit point.

    Attributes
    ----------
    id : int
        Unique identifier for this block
    block_type : BlockType
        Type of this basic block
    label : str
        Human-readable label for the block
    statements : List[str]
        List of Fortran statements in this block
    condition : Optional[str]
        Condition expression for conditional blocks (IF, DO WHILE, etc.)
    successors : List[int]
        IDs of blocks that can follow this one
    predecessors : List[int]
        IDs of blocks that can precede this one
    """

    id: int
    block_type: BlockType
    label: str
    statements: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    successors: List[int] = field(default_factory=list)
    predecessors: List[int] = field(default_factory=list)


class ControlFlowGraph:
    """Control flow graph for a Fortran procedure

    This class represents the control flow within a subroutine or function,
    showing how different parts of the code connect through conditional
    branches and loops.

    Parameters
    ----------
    procedure_name : str
        Name of the procedure this CFG represents
    procedure_type : str
        Type of procedure ('subroutine' or 'function')
    """

    def __init__(self, procedure_name: str, procedure_type: str):
        self.procedure_name = procedure_name
        self.procedure_type = procedure_type
        self.blocks: Dict[int, BasicBlock] = {}
        self.entry_block_id: Optional[int] = None
        self.exit_block_id: Optional[int] = None
        self._next_block_id = 0

    def create_block(
        self, block_type: BlockType, label: str, condition: Optional[str] = None
    ) -> BasicBlock:
        """Create a new basic block and add it to the graph"""
        block_id = self._next_block_id
        self._next_block_id += 1

        block = BasicBlock(
            id=block_id, block_type=block_type, label=label, condition=condition
        )
        self.blocks[block_id] = block
        return block

    def add_edge(self, from_id: int, to_id: int) -> None:
        """Add a directed edge between two blocks"""
        if from_id not in self.blocks or to_id not in self.blocks:
            return

        if to_id not in self.blocks[from_id].successors:
            self.blocks[from_id].successors.append(to_id)

        if from_id not in self.blocks[to_id].predecessors:
            self.blocks[to_id].predecessors.append(from_id)


class FortranControlFlowParser:
    """Parser for extracting control flow from Fortran source code

    This parser analyzes Fortran subroutines and functions to identify
    control flow structures and build a control flow graph.

    Parameters
    ----------
    source_code : str
        The Fortran source code to parse
    procedure_name : str
        Name of the procedure
    procedure_type : str
        Type of procedure ('subroutine' or 'function')
    """

    # Regular expressions for Fortran control flow statements
    IF_THEN_RE = re.compile(
        r"^\s*(?:(\w+)\s*:)?\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE
    )
    ELSE_IF_RE = re.compile(r"^\s*else\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE)
    ELSE_RE = re.compile(r"^\s*else\s*$", re.IGNORECASE)
    END_IF_RE = re.compile(r"^\s*end\s*if(?:\s+(\w+))?\s*$", re.IGNORECASE)

    DO_LOOP_RE = re.compile(r"^\s*(?:(\w+)\s*:)?\s*do\s+(.*)$", re.IGNORECASE)
    END_DO_RE = re.compile(r"^\s*end\s*do(?:\s+(\w+))?\s*$", re.IGNORECASE)

    SELECT_CASE_RE = re.compile(
        r"^\s*(?:(\w+)\s*:)?\s*select\s+case\s*\((.*?)\)\s*$", re.IGNORECASE
    )
    CASE_RE = re.compile(r"^\s*case\s*\((.*?)\)\s*$", re.IGNORECASE)
    CASE_DEFAULT_RE = re.compile(r"^\s*case\s+default\s*$", re.IGNORECASE)
    END_SELECT_RE = re.compile(r"^\s*end\s*select(?:\s+(\w+))?\s*$", re.IGNORECASE)

    # Single-line IF statement
    SINGLE_IF_RE = re.compile(r"^\s*if\s*\((.*?)\)\s+(.+)$", re.IGNORECASE)

    # RETURN statement
    RETURN_RE = re.compile(r"^\s*return\s*$", re.IGNORECASE)

    def __init__(self, source_code: str, procedure_name: str, procedure_type: str):
        self.source_code = source_code
        self.procedure_name = procedure_name
        self.procedure_type = procedure_type
        self.cfg = ControlFlowGraph(procedure_name, procedure_type)

    def parse(self) -> ControlFlowGraph:
        """Parse the source code and build the control flow graph"""
        lines = self._preprocess_source()

        # Create entry and exit blocks
        entry = self.cfg.create_block(BlockType.ENTRY, "Entry")
        self.cfg.entry_block_id = entry.id

        exit_block = self.cfg.create_block(BlockType.EXIT, "Return")
        self.cfg.exit_block_id = exit_block.id

        # Parse the procedure body
        current_block = entry
        i = 0

        # Stack for tracking nested structures
        control_stack: List[Tuple[str, BasicBlock, Optional[BasicBlock]]] = []

        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()

            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith("!"):
                i += 1
                continue

            # Check for IF-THEN-ELSE blocks
            if match := self.IF_THEN_RE.match(line_stripped):
                label, condition = match.groups()

                # Create condition block
                cond_block = self.cfg.create_block(
                    BlockType.IF_CONDITION, f"IF ({condition})", condition=condition
                )
                self.cfg.add_edge(current_block.id, cond_block.id)

                # Create then block
                then_block = self.cfg.create_block(BlockType.STATEMENT, "THEN")
                self.cfg.add_edge(cond_block.id, then_block.id)

                # Create merge block for after the if
                merge_block = self.cfg.create_block(BlockType.STATEMENT, "After IF")

                # Push onto stack (third element tracks if else was seen)
                control_stack.append(("if", cond_block, merge_block, False))
                current_block = then_block

            elif self.ELSE_IF_RE.match(line_stripped):
                match = self.ELSE_IF_RE.match(line_stripped)
                condition = match.group(1)

                if control_stack and control_stack[-1][0] == "if":
                    _, cond_block, merge_block, _ = control_stack[-1]

                    # Connect current block to merge
                    self.cfg.add_edge(current_block.id, merge_block.id)

                    # Create else-if condition block
                    elseif_cond = self.cfg.create_block(
                        BlockType.IF_CONDITION,
                        f"ELSE IF ({condition})",
                        condition=condition,
                    )
                    self.cfg.add_edge(cond_block.id, elseif_cond.id)

                    # Create block for else-if body
                    elseif_body = self.cfg.create_block(
                        BlockType.STATEMENT, "ELSE IF body"
                    )
                    self.cfg.add_edge(elseif_cond.id, elseif_body.id)

                    # Update stack (still no else seen)
                    control_stack[-1] = ("if", elseif_cond, merge_block, False)
                    current_block = elseif_body

            elif self.ELSE_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == "if":
                    _, cond_block, merge_block, _ = control_stack[-1]

                    # Connect current block to merge
                    self.cfg.add_edge(current_block.id, merge_block.id)

                    # Create else block
                    else_block = self.cfg.create_block(BlockType.STATEMENT, "ELSE")
                    self.cfg.add_edge(cond_block.id, else_block.id)
                    # Mark that we've seen an else
                    control_stack[-1] = ("if", cond_block, merge_block, True)
                    current_block = else_block

            elif self.END_IF_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == "if":
                    _, cond_block, merge_block, has_else = control_stack.pop()

                    # Connect current block to merge
                    self.cfg.add_edge(current_block.id, merge_block.id)

                    # If no else was seen, connect condition to merge (false branch)
                    if not has_else:
                        self.cfg.add_edge(cond_block.id, merge_block.id)

                    current_block = merge_block

            # Check for DO loops
            elif match := self.DO_LOOP_RE.match(line_stripped):
                label, loop_control = match.groups()

                # Create loop header block
                loop_header = self.cfg.create_block(
                    BlockType.DO_LOOP, f"DO {loop_control}", condition=loop_control
                )
                self.cfg.add_edge(current_block.id, loop_header.id)

                # Create loop body block
                loop_body = self.cfg.create_block(BlockType.STATEMENT, "Loop body")
                self.cfg.add_edge(loop_header.id, loop_body.id)

                # Create after-loop block
                after_loop = self.cfg.create_block(BlockType.STATEMENT, "After loop")
                self.cfg.add_edge(loop_header.id, after_loop.id)

                # Push onto stack
                control_stack.append(("do", loop_header, after_loop))
                current_block = loop_body

            elif self.END_DO_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == "do":
                    _, loop_header, after_loop = control_stack.pop()

                    # Create back-edge to loop header
                    self.cfg.add_edge(current_block.id, loop_header.id)
                    current_block = after_loop

            # Check for SELECT CASE
            elif match := self.SELECT_CASE_RE.match(line_stripped):
                label, select_expr = match.groups()

                # Create select block
                select_block = self.cfg.create_block(
                    BlockType.SELECT_CASE,
                    f"SELECT CASE ({select_expr})",
                    condition=select_expr,
                )
                self.cfg.add_edge(current_block.id, select_block.id)

                # Create after-select block
                after_select = self.cfg.create_block(
                    BlockType.STATEMENT, "After SELECT"
                )

                # Push onto stack
                control_stack.append(("select", select_block, after_select))
                current_block = select_block

            elif self.CASE_RE.match(line_stripped) or self.CASE_DEFAULT_RE.match(
                line_stripped
            ):
                if control_stack and control_stack[-1][0] == "select":
                    _, select_block, after_select = control_stack[-1]

                    # Connect previous case to after-select
                    if current_block != select_block:
                        self.cfg.add_edge(current_block.id, after_select.id)

                    # Parse case value
                    case_match = self.CASE_RE.match(line_stripped)
                    if case_match:
                        case_value = case_match.group(1)
                        case_label = f"CASE ({case_value})"
                    else:
                        case_value = "DEFAULT"
                        case_label = "CASE DEFAULT"

                    # Create case block
                    case_block = self.cfg.create_block(
                        BlockType.CASE, case_label, condition=case_value
                    )
                    self.cfg.add_edge(select_block.id, case_block.id)
                    current_block = case_block

            elif self.END_SELECT_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == "select":
                    _, _, after_select = control_stack.pop()

                    # Connect current case to after-select
                    self.cfg.add_edge(current_block.id, after_select.id)
                    current_block = after_select

            # Single-line IF statement
            elif match := self.SINGLE_IF_RE.match(line_stripped):
                condition, statement = match.groups()

                # Don't process if it's an IF-THEN (already handled above)
                if not statement.strip().lower() == "then":
                    # Create condition block
                    cond_block = self.cfg.create_block(
                        BlockType.IF_CONDITION, f"IF ({condition})", condition=condition
                    )
                    self.cfg.add_edge(current_block.id, cond_block.id)

                    # Create statement block
                    stmt_block = self.cfg.create_block(
                        BlockType.STATEMENT, statement[:50]  # Truncate long statements
                    )
                    stmt_block.statements.append(statement)
                    self.cfg.add_edge(cond_block.id, stmt_block.id)

                    # Create merge block
                    merge_block = self.cfg.create_block(BlockType.STATEMENT, "Continue")
                    self.cfg.add_edge(stmt_block.id, merge_block.id)
                    self.cfg.add_edge(cond_block.id, merge_block.id)

                    current_block = merge_block

            # Check for RETURN statement
            elif self.RETURN_RE.match(line_stripped):
                # Create a return block
                return_block = self.cfg.create_block(BlockType.RETURN, "RETURN")
                self.cfg.add_edge(current_block.id, return_block.id)
                
                # Connect return block directly to exit
                self.cfg.add_edge(return_block.id, exit_block.id)
                
                # Create a new statement block for any code after return (unreachable but parse it)
                current_block = self.cfg.create_block(BlockType.STATEMENT, "After RETURN")

            else:
                # Regular statement
                if current_block.block_type == BlockType.STATEMENT:
                    current_block.statements.append(line_stripped)
                else:
                    # Create a new statement block
                    stmt_block = self.cfg.create_block(
                        BlockType.STATEMENT,
                        line_stripped[:50],  # Truncate long statements
                    )
                    stmt_block.statements.append(line_stripped)
                    self.cfg.add_edge(current_block.id, stmt_block.id)
                    current_block = stmt_block

            i += 1

        # Connect final block to exit
        if current_block.id != exit_block.id:
            self.cfg.add_edge(current_block.id, exit_block.id)

        return self.cfg

    def _preprocess_source(self) -> List[str]:
        """Preprocess source code to extract the procedure body

        Returns a list of lines containing only the procedure body,
        excluding the procedure declaration and end statement.
        """
        lines = self.source_code.split("\n")
        result = []
        in_procedure = False

        # Patterns to match procedure start and end
        proc_start = re.compile(
            rf"^\s*{re.escape(self.procedure_type)}\s+{re.escape(self.procedure_name)}\b",
            re.IGNORECASE,
        )
        proc_end = re.compile(
            rf"^\s*end\s+{re.escape(self.procedure_type)}\b", re.IGNORECASE
        )
        contains_re = re.compile(r"^\s*contains\s*$", re.IGNORECASE)

        for line in lines:
            if proc_start.match(line.strip()):
                in_procedure = True
                continue

            if in_procedure:
                # Stop at 'contains' or 'end subroutine/function'
                if contains_re.match(line.strip()) or proc_end.match(line.strip()):
                    break

                result.append(line)

        return result


def parse_control_flow(
    source_code: str, procedure_name: str, procedure_type: str
) -> Optional[ControlFlowGraph]:
    """Parse control flow from Fortran procedure source code

    Parameters
    ----------
    source_code : str
        The complete source code of the procedure
    procedure_name : str
        Name of the procedure
    procedure_type : str
        Type of procedure ('subroutine' or 'function')

    Returns
    -------
    ControlFlowGraph or None
        The control flow graph, or None if parsing fails
    """
    try:
        parser = FortranControlFlowParser(source_code, procedure_name, procedure_type)
        return parser.parse()
    except Exception:
        return None


@dataclass
class AllocationSummary:
    """Summary of allocations and deallocations grouped by variable

    Attributes
    ----------
    variable_name : str
        Name of the variable being allocated/deallocated
    allocate_lines : List[int]
        Line numbers where this variable is allocated
    deallocate_lines : List[int]
        Line numbers where this variable is deallocated
    """

    variable_name: str
    allocate_lines: List[int] = field(default_factory=list)
    deallocate_lines: List[int] = field(default_factory=list)


@dataclass
class LogicBlock:
    """Represents a logic block in a procedure for hierarchical display

    Attributes
    ----------
    block_type : str
        Type of block (e.g., 'if', 'do', 'select', 'case', 'else', 'statements')
    condition : Optional[str]
        Condition or control expression (for IF, DO, SELECT CASE, etc.)
    statements : List[str]
        Statements within this block (before any nested blocks)
    children : List[LogicBlock]
        Nested logic blocks within this one
    level : int
        Nesting level (0 for top-level)
    label : Optional[str]
        Optional Fortran label
    start_line : Optional[int]
        Starting line number of this block (1-indexed)
    end_line : Optional[int]
        Ending line number of this block (1-indexed)
    statement_lines : List[int]
        Line numbers corresponding to each statement
    comments : List[str]
        Documentation comments (!! comments) associated with this block
    comment_lines : List[int]
        Line numbers corresponding to each comment
    """

    block_type: str
    condition: Optional[str] = None
    statements: List[str] = field(default_factory=list)
    children: List["LogicBlock"] = field(default_factory=list)
    level: int = 0
    label: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    statement_lines: List[int] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    comment_lines: List[int] = field(default_factory=list)


class LogicBlockExtractor:
    """Extracts logic blocks from Fortran source code in hierarchical form

    This extracts control structures and organizes them hierarchically
    as they appear in the source code, suitable for display in the UI.
    """

    # Regular expressions for control flow statements
    IF_THEN_RE = re.compile(
        r"^\s*(?:(\w+)\s*:)?\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE
    )
    ELSE_IF_RE = re.compile(r"^\s*else\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE)
    ELSE_RE = re.compile(r"^\s*else\s*$", re.IGNORECASE)
    END_IF_RE = re.compile(r"^\s*end\s*if(?:\s+(\w+))?\s*$", re.IGNORECASE)

    DO_LOOP_RE = re.compile(r"^\s*(?:(\w+)\s*:)?\s*do\s+(.*)$", re.IGNORECASE)
    END_DO_RE = re.compile(r"^\s*end\s*do(?:\s+(\w+))?\s*$", re.IGNORECASE)

    SELECT_CASE_RE = re.compile(
        r"^\s*(?:(\w+)\s*:)?\s*select\s+case\s*\((.*?)\)\s*$", re.IGNORECASE
    )
    CASE_RE = re.compile(r"^\s*case\s*\((.*?)\)\s*$", re.IGNORECASE)
    CASE_DEFAULT_RE = re.compile(r"^\s*case\s+default\s*$", re.IGNORECASE)
    END_SELECT_RE = re.compile(r"^\s*end\s*select(?:\s+(\w+))?\s*$", re.IGNORECASE)

    # RETURN statement
    RETURN_RE = re.compile(r"^\s*return\s*$", re.IGNORECASE)

    # Regular expressions for statements to exclude from logic blocks
    USE_RE = re.compile(r"^\s*use\s+", re.IGNORECASE)
    IMPLICIT_RE = re.compile(r"^\s*implicit\s+", re.IGNORECASE)
    # Match variable declarations (type declarations)
    # Matches: integer, real, double precision, complex, logical, character, class, procedure, type(...)
    DECLARATION_RE = re.compile(
        r"^\s*(?:integer|real|double\s+precision|complex|logical|character|class|procedure|type\s*\()",
        re.IGNORECASE,
    )

    # Regular expressions for allocation/deallocation statements
    ALLOCATE_RE = re.compile(r"^\s*allocate\s*\((.*?)\)", re.IGNORECASE)
    DEALLOCATE_RE = re.compile(r"^\s*deallocate\s*\((.*?)\)", re.IGNORECASE)

    def __init__(self, source_code: str, procedure_name: str, procedure_type: str):
        self.source_code = source_code
        self.procedure_name = procedure_name
        self.procedure_type = procedure_type
        self.allocations: Dict[str, AllocationSummary] = {}

    def _is_declaration_or_use(self, line_stripped: str) -> bool:
        """Check if a line is a USE, IMPLICIT, or type declaration statement

        Parameters
        ----------
        line_stripped : str
            The stripped line to check

        Returns
        -------
        bool
            True if the line is a declaration/use statement, False otherwise
        """
        return (
            self.USE_RE.match(line_stripped)
            or self.IMPLICIT_RE.match(line_stripped)
            or self.DECLARATION_RE.match(line_stripped)
        )

    def _extract_variable_names(self, alloc_content: str) -> List[str]:
        """Extract variable names from allocation statement content

        Parameters
        ----------
        alloc_content : str
            The content inside allocate() or deallocate() parentheses

        Returns
        -------
        List[str]
            List of variable names being allocated/deallocated
        """
        variables = []
        # Split by comma, but need to handle nested parentheses
        parts = []
        current = []
        paren_depth = 0

        for char in alloc_content:
            if char == "(":
                paren_depth += 1
                current.append(char)
            elif char == ")":
                paren_depth -= 1
                current.append(char)
            elif char == "," and paren_depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        # Extract variable name from each part
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Variable name is the first identifier before ( or =
            # Examples: "hru(10)", "res", "var = value"
            var_match = re.match(r"^([a-zA-Z_]\w*)", part)
            if var_match:
                variables.append(var_match.group(1))

        return variables

    def _track_allocation(self, line_stripped: str, line_num: int):
        """Track allocation/deallocation statements

        Parameters
        ----------
        line_stripped : str
            The stripped line to check
        line_num : int
            Line number (1-indexed)
        """
        # Check for allocate statement
        if match := self.ALLOCATE_RE.search(line_stripped):
            alloc_content = match.group(1)
            variables = self._extract_variable_names(alloc_content)
            for var in variables:
                if var not in self.allocations:
                    self.allocations[var] = AllocationSummary(variable_name=var)
                self.allocations[var].allocate_lines.append(line_num)

        # Check for deallocate statement
        elif match := self.DEALLOCATE_RE.search(line_stripped):
            dealloc_content = match.group(1)
            variables = self._extract_variable_names(dealloc_content)
            for var in variables:
                if var not in self.allocations:
                    self.allocations[var] = AllocationSummary(variable_name=var)
                self.allocations[var].deallocate_lines.append(line_num)

    def extract(self) -> List[LogicBlock]:
        """Extract logic blocks from the source code

        Returns
        -------
        List[LogicBlock]
            List of top-level logic blocks
        """
        lines, line_numbers = self._preprocess_source()
        blocks: List[LogicBlock] = []

        if not lines:
            return blocks

        # Stack to track nested blocks: (block, current_statements, current_statement_lines, current_comments, current_comment_lines)
        stack: List[Tuple[LogicBlock, List[str], List[int], List[str], List[int]]] = []
        current_statements: List[str] = []
        current_statement_lines: List[int] = []
        current_comments: List[str] = []
        current_comment_lines: List[int] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = line_numbers[i]
            line_stripped = line.strip()

            # Collect documentation comments (!! comments)
            if line_stripped.startswith("!!"):
                # Strip the !! prefix and add to current comments
                comment_text = line_stripped[2:].strip()
                current_comments.append(comment_text)
                current_comment_lines.append(line_num)
                i += 1
                continue

            # Skip empty lines and other comments (single !)
            if not line_stripped or (
                line_stripped.startswith("!") and not line_stripped.startswith("!!")
            ):
                i += 1
                continue

            # Check for IF-THEN-ELSE blocks
            if match := self.IF_THEN_RE.match(line_stripped):
                label, condition = match.groups()

                # Create IF block
                if_block = LogicBlock(
                    block_type="if",
                    condition=condition,
                    level=len(stack),
                    label=label,
                    start_line=line_num,
                    comments=current_comments.copy(),
                    comment_lines=current_comment_lines.copy(),
                )

                # Save current statements to parent or top-level
                if stack:
                    stack[-1][1].extend(current_statements)
                    stack[-1][2].extend(current_statement_lines)
                    stack[-1][3].extend(current_comments)
                    stack[-1][4].extend(current_comment_lines)
                    stack[-1][3].extend(current_comments)
                    stack[-1][4].extend(current_comment_lines)
                else:
                    if current_statements:
                        blocks.append(
                            LogicBlock(
                                block_type="statements",
                                statements=current_statements,
                                level=0,
                                statement_lines=current_statement_lines,
                                comments=current_comments,
                                comment_lines=current_comment_lines,
                            )
                        )
                current_statements = []
                current_statement_lines = []
                current_comments = []
                current_comment_lines = []
                current_comments = []
                current_comment_lines = []

                # Push to stack
                stack.append((if_block, [], [], [], []))

            elif self.ELSE_IF_RE.match(line_stripped):
                match = self.ELSE_IF_RE.match(line_stripped)
                condition = match.group(1)

                if stack and stack[-1][0].block_type in ["if", "elseif"]:
                    # Save statements to current IF/ELSEIF block
                    stack[-1][0].statements = stack[-1][1]
                    stack[-1][0].statement_lines = stack[-1][2]
                    stack[-1][0].comments = stack[-1][3]
                    stack[-1][0].comment_lines = stack[-1][4]
                    stack[-1][0].end_line = line_num - 1

                    # Create ELSE IF block
                    elseif_block = LogicBlock(
                        block_type="elseif",
                        condition=condition,
                        level=stack[-1][0].level,
                        start_line=line_num,
                    )

                    # Get parent level
                    if len(stack) > 1:
                        stack[-2][0].children.append(stack[-1][0])
                        stack.pop()
                        stack.append((elseif_block, [], [], [], []))
                    else:
                        blocks.append(stack[-1][0])
                        stack.pop()
                        stack.append((elseif_block, [], [], [], []))

            elif self.ELSE_RE.match(line_stripped):
                if stack and stack[-1][0].block_type in ["if", "elseif"]:
                    # Save statements to current IF/ELSEIF block
                    stack[-1][0].statements = stack[-1][1]
                    stack[-1][0].statement_lines = stack[-1][2]
                    stack[-1][0].comments = stack[-1][3]
                    stack[-1][0].comment_lines = stack[-1][4]
                    stack[-1][0].end_line = line_num - 1

                    # Create ELSE block at same level
                    else_block = LogicBlock(
                        block_type="else", level=stack[-1][0].level, start_line=line_num
                    )

                    # Add current block to parent and push ELSE
                    if len(stack) > 1:
                        stack[-2][0].children.append(stack[-1][0])
                        stack.pop()
                        stack.append((else_block, [], [], [], []))
                    else:
                        blocks.append(stack[-1][0])
                        stack.pop()
                        stack.append((else_block, [], [], [], []))

            elif self.END_IF_RE.match(line_stripped):
                if stack and stack[-1][0].block_type in ["if", "elseif", "else"]:
                    # Save statements to current block
                    stack[-1][0].statements = stack[-1][1]
                    stack[-1][0].statement_lines = stack[-1][2]
                    stack[-1][0].comments = stack[-1][3]
                    stack[-1][0].comment_lines = stack[-1][4]
                    stack[-1][0].end_line = line_num

                    # Pop and add to parent
                    block, _, _, _, _ = stack.pop()
                    if stack:
                        stack[-1][0].children.append(block)
                    else:
                        blocks.append(block)

            # Check for DO loops
            elif match := self.DO_LOOP_RE.match(line_stripped):
                label, loop_control = match.groups()

                # Create DO block
                do_block = LogicBlock(
                    block_type="do",
                    condition=loop_control,
                    level=len(stack),
                    label=label,
                    start_line=line_num,
                    comments=current_comments.copy(),
                    comment_lines=current_comment_lines.copy(),
                )

                # Save current statements
                if stack:
                    stack[-1][1].extend(current_statements)
                    stack[-1][2].extend(current_statement_lines)
                    stack[-1][3].extend(current_comments)
                    stack[-1][4].extend(current_comment_lines)
                else:
                    if current_statements:
                        blocks.append(
                            LogicBlock(
                                block_type="statements",
                                statements=current_statements,
                                level=0,
                                statement_lines=current_statement_lines,
                                comments=current_comments,
                                comment_lines=current_comment_lines,
                            )
                        )
                current_statements = []
                current_statement_lines = []
                current_comments = []
                current_comment_lines = []

                # Push to stack
                stack.append((do_block, [], [], [], []))

            elif self.END_DO_RE.match(line_stripped):
                if stack and stack[-1][0].block_type == "do":
                    # Save statements to DO block
                    stack[-1][0].statements = stack[-1][1]
                    stack[-1][0].statement_lines = stack[-1][2]
                    stack[-1][0].comments = stack[-1][3]
                    stack[-1][0].comment_lines = stack[-1][4]
                    stack[-1][0].end_line = line_num

                    # Pop and add to parent
                    do_block, _, _, _, _ = stack.pop()
                    if stack:
                        stack[-1][0].children.append(do_block)
                    else:
                        blocks.append(do_block)

            # Check for SELECT CASE
            elif match := self.SELECT_CASE_RE.match(line_stripped):
                label, select_expr = match.groups()

                # Create SELECT block
                select_block = LogicBlock(
                    block_type="select",
                    condition=select_expr,
                    level=len(stack),
                    label=label,
                    start_line=line_num,
                    comments=current_comments.copy(),
                    comment_lines=current_comment_lines.copy(),
                )

                # Save current statements
                if stack:
                    stack[-1][1].extend(current_statements)
                    stack[-1][2].extend(current_statement_lines)
                    stack[-1][3].extend(current_comments)
                    stack[-1][4].extend(current_comment_lines)
                else:
                    if current_statements:
                        blocks.append(
                            LogicBlock(
                                block_type="statements",
                                statements=current_statements,
                                level=0,
                                statement_lines=current_statement_lines,
                                comments=current_comments,
                                comment_lines=current_comment_lines,
                            )
                        )
                current_statements = []
                current_statement_lines = []
                current_comments = []
                current_comment_lines = []

                # Push to stack
                stack.append((select_block, [], [], [], []))

            elif self.CASE_RE.match(line_stripped) or self.CASE_DEFAULT_RE.match(
                line_stripped
            ):
                if stack and stack[-1][0].block_type in ["select", "case"]:
                    # If we were in a previous CASE, save it
                    if stack[-1][0].block_type == "case":
                        stack[-1][0].statements = stack[-1][1]
                        stack[-1][0].statement_lines = stack[-1][2]
                        stack[-1][0].comments = stack[-1][3]
                        stack[-1][0].comment_lines = stack[-1][4]
                        stack[-1][0].end_line = line_num - 1
                        case_block, _, _, _, _ = stack.pop()
                        stack[-1][0].children.append(case_block)

                    # Parse case value
                    case_match = self.CASE_RE.match(line_stripped)
                    if case_match:
                        case_value = case_match.group(1)
                    else:
                        case_value = "DEFAULT"

                    # Create CASE block
                    case_block = LogicBlock(
                        block_type="case",
                        condition=case_value,
                        level=len(stack),
                        start_line=line_num,
                        comments=current_comments.copy(),
                        comment_lines=current_comment_lines.copy(),
                    )
                    current_comments = []
                    current_comment_lines = []
                    stack.append((case_block, [], [], [], []))

            elif self.END_SELECT_RE.match(line_stripped):
                if stack:
                    # Close any open CASE
                    if stack[-1][0].block_type == "case":
                        stack[-1][0].statements = stack[-1][1]
                        stack[-1][0].statement_lines = stack[-1][2]
                        stack[-1][0].comments = stack[-1][3]
                        stack[-1][0].comment_lines = stack[-1][4]
                        stack[-1][0].end_line = line_num - 1
                        case_block, _, _, _, _ = stack.pop()
                        stack[-1][0].children.append(case_block)

                    # Close SELECT - Add END SELECT to the block
                    if stack and stack[-1][0].block_type == "select":
                        stack[-1][0].end_line = line_num
                        # Note: END SELECT is not added as a statement to match Fortran structure
                        select_block, _, _, _, _ = stack.pop()
                        if stack:
                            stack[-1][0].children.append(select_block)
                        else:
                            blocks.append(select_block)

            else:
                # Regular statement - skip USE, IMPLICIT, and declarations
                if not self._is_declaration_or_use(line_stripped):
                    # Track allocation/deallocation statements
                    self._track_allocation(line_stripped, line_num)

                    if stack:
                        # We're inside a block, add to that block's statements
                        # First add any accumulated comments
                        if current_comments:
                            stack[-1][3].extend(current_comments)
                            stack[-1][4].extend(current_comment_lines)
                            current_comments = []
                            current_comment_lines = []
                        stack[-1][1].append(line_stripped)
                        stack[-1][2].append(line_num)
                    else:
                        # We're at top level
                        current_statements.append(line_stripped)
                        current_statement_lines.append(line_num)

            i += 1

        # Add any remaining statements
        if current_statements:
            if stack:
                stack[-1][1].extend(current_statements)
                stack[-1][2].extend(current_statement_lines)
                stack[-1][3].extend(current_comments)
                stack[-1][4].extend(current_comment_lines)
            else:
                blocks.append(
                    LogicBlock(
                        block_type="statements",
                        statements=current_statements,
                        level=0,
                        statement_lines=current_statement_lines,
                        comments=current_comments,
                        comment_lines=current_comment_lines,
                    )
                )

        # Close any unclosed blocks (shouldn't happen in valid code)
        while stack:
            block, stmts, stmt_lines, cmts, cmt_lines = stack.pop()
            block.statements = stmts
            block.statement_lines = stmt_lines
            block.comments = cmts
            block.comment_lines = cmt_lines
            if stack:
                stack[-1][0].children.append(block)
            else:
                blocks.append(block)

        return blocks

    def _preprocess_source(self) -> Tuple[List[str], List[int]]:
        """Preprocess source code to extract the procedure body

        Returns
        -------
        Tuple[List[str], List[int]]
            List of lines and their corresponding line numbers (1-indexed)
        """
        lines = self.source_code.split("\n")
        result = []
        line_numbers = []
        in_procedure = False

        # Patterns to match procedure start and end
        proc_start = re.compile(
            rf"^\s*{re.escape(self.procedure_type)}\s+{re.escape(self.procedure_name)}\b",
            re.IGNORECASE,
        )
        proc_end = re.compile(
            rf"^\s*end\s+{re.escape(self.procedure_type)}\b", re.IGNORECASE
        )
        contains_re = re.compile(r"^\s*contains\s*$", re.IGNORECASE)

        for line_num, line in enumerate(lines, start=1):
            if proc_start.match(line.strip()):
                in_procedure = True
                continue

            if in_procedure:
                # Stop at 'contains' or 'end subroutine/function'
                if contains_re.match(line.strip()) or proc_end.match(line.strip()):
                    break

                result.append(line)
                line_numbers.append(line_num)

        return result, line_numbers


def extract_logic_blocks(
    source_code: str, procedure_name: str, procedure_type: str
) -> Optional[Tuple[List[LogicBlock], List[AllocationSummary]]]:
    """Extract logic blocks from Fortran procedure source code

    Parameters
    ----------
    source_code : str
        The complete source code of the procedure
    procedure_name : str
        Name of the procedure
    procedure_type : str
        Type of procedure ('subroutine' or 'function')

    Returns
    -------
    Tuple[List[LogicBlock], List[AllocationSummary]] or None
        Tuple of (list of logic blocks, list of allocation summaries), or None if extraction fails
    """
    try:
        extractor = LogicBlockExtractor(source_code, procedure_name, procedure_type)
        blocks = extractor.extract()
        allocations = list(extractor.allocations.values())
        return (blocks, allocations)
    except Exception:
        return None
