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
        self,
        block_type: BlockType,
        label: str,
        condition: Optional[str] = None
    ) -> BasicBlock:
        """Create a new basic block and add it to the graph"""
        block_id = self._next_block_id
        self._next_block_id += 1
        
        block = BasicBlock(
            id=block_id,
            block_type=block_type,
            label=label,
            condition=condition
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
        r'^\s*(?:(\w+)\s*:)?\s*if\s*\((.*?)\)\s*then\s*$',
        re.IGNORECASE
    )
    ELSE_IF_RE = re.compile(
        r'^\s*else\s*if\s*\((.*?)\)\s*then\s*$',
        re.IGNORECASE
    )
    ELSE_RE = re.compile(r'^\s*else\s*$', re.IGNORECASE)
    END_IF_RE = re.compile(r'^\s*end\s*if(?:\s+(\w+))?\s*$', re.IGNORECASE)
    
    DO_LOOP_RE = re.compile(
        r'^\s*(?:(\w+)\s*:)?\s*do\s+(.*)$',
        re.IGNORECASE
    )
    END_DO_RE = re.compile(r'^\s*end\s*do(?:\s+(\w+))?\s*$', re.IGNORECASE)
    
    SELECT_CASE_RE = re.compile(
        r'^\s*(?:(\w+)\s*:)?\s*select\s+case\s*\((.*?)\)\s*$',
        re.IGNORECASE
    )
    CASE_RE = re.compile(
        r'^\s*case\s*\((.*?)\)\s*$',
        re.IGNORECASE
    )
    CASE_DEFAULT_RE = re.compile(r'^\s*case\s+default\s*$', re.IGNORECASE)
    END_SELECT_RE = re.compile(
        r'^\s*end\s*select(?:\s+(\w+))?\s*$',
        re.IGNORECASE
    )
    
    # Single-line IF statement
    SINGLE_IF_RE = re.compile(
        r'^\s*if\s*\((.*?)\)\s+(.+)$',
        re.IGNORECASE
    )
    
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
        
        exit_block = self.cfg.create_block(BlockType.EXIT, "Exit")
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
            if not line_stripped or line_stripped.startswith('!'):
                i += 1
                continue
            
            # Check for IF-THEN-ELSE blocks
            if match := self.IF_THEN_RE.match(line_stripped):
                label, condition = match.groups()
                
                # Create condition block
                cond_block = self.cfg.create_block(
                    BlockType.IF_CONDITION,
                    f"IF ({condition})",
                    condition=condition
                )
                self.cfg.add_edge(current_block.id, cond_block.id)
                
                # Create then block
                then_block = self.cfg.create_block(
                    BlockType.STATEMENT,
                    "THEN"
                )
                self.cfg.add_edge(cond_block.id, then_block.id)
                
                # Create merge block for after the if
                merge_block = self.cfg.create_block(
                    BlockType.STATEMENT,
                    "After IF"
                )
                
                # Push onto stack (third element tracks if else was seen)
                control_stack.append(('if', cond_block, merge_block, False))
                current_block = then_block
                
            elif self.ELSE_IF_RE.match(line_stripped):
                match = self.ELSE_IF_RE.match(line_stripped)
                condition = match.group(1)
                
                if control_stack and control_stack[-1][0] == 'if':
                    _, cond_block, merge_block, _ = control_stack[-1]
                    
                    # Connect current block to merge
                    self.cfg.add_edge(current_block.id, merge_block.id)
                    
                    # Create else-if condition block
                    elseif_cond = self.cfg.create_block(
                        BlockType.IF_CONDITION,
                        f"ELSE IF ({condition})",
                        condition=condition
                    )
                    self.cfg.add_edge(cond_block.id, elseif_cond.id)
                    
                    # Create block for else-if body
                    elseif_body = self.cfg.create_block(
                        BlockType.STATEMENT,
                        "ELSE IF body"
                    )
                    self.cfg.add_edge(elseif_cond.id, elseif_body.id)
                    
                    # Update stack (still no else seen)
                    control_stack[-1] = ('if', elseif_cond, merge_block, False)
                    current_block = elseif_body
                    
            elif self.ELSE_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == 'if':
                    _, cond_block, merge_block, _ = control_stack[-1]
                    
                    # Connect current block to merge
                    self.cfg.add_edge(current_block.id, merge_block.id)
                    
                    # Create else block
                    else_block = self.cfg.create_block(
                        BlockType.STATEMENT,
                        "ELSE"
                    )
                    self.cfg.add_edge(cond_block.id, else_block.id)
                    # Mark that we've seen an else
                    control_stack[-1] = ('if', cond_block, merge_block, True)
                    current_block = else_block
                    
            elif self.END_IF_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == 'if':
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
                    BlockType.DO_LOOP,
                    f"DO {loop_control}",
                    condition=loop_control
                )
                self.cfg.add_edge(current_block.id, loop_header.id)
                
                # Create loop body block
                loop_body = self.cfg.create_block(
                    BlockType.STATEMENT,
                    "Loop body"
                )
                self.cfg.add_edge(loop_header.id, loop_body.id)
                
                # Create after-loop block
                after_loop = self.cfg.create_block(
                    BlockType.STATEMENT,
                    "After loop"
                )
                self.cfg.add_edge(loop_header.id, after_loop.id)
                
                # Push onto stack
                control_stack.append(('do', loop_header, after_loop))
                current_block = loop_body
                
            elif self.END_DO_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == 'do':
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
                    condition=select_expr
                )
                self.cfg.add_edge(current_block.id, select_block.id)
                
                # Create after-select block
                after_select = self.cfg.create_block(
                    BlockType.STATEMENT,
                    "After SELECT"
                )
                
                # Push onto stack
                control_stack.append(('select', select_block, after_select))
                current_block = select_block
                
            elif self.CASE_RE.match(line_stripped) or self.CASE_DEFAULT_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == 'select':
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
                        BlockType.CASE,
                        case_label,
                        condition=case_value
                    )
                    self.cfg.add_edge(select_block.id, case_block.id)
                    current_block = case_block
                    
            elif self.END_SELECT_RE.match(line_stripped):
                if control_stack and control_stack[-1][0] == 'select':
                    _, _, after_select = control_stack.pop()
                    
                    # Connect current case to after-select
                    self.cfg.add_edge(current_block.id, after_select.id)
                    current_block = after_select
                    
            # Single-line IF statement
            elif match := self.SINGLE_IF_RE.match(line_stripped):
                condition, statement = match.groups()
                
                # Don't process if it's an IF-THEN (already handled above)
                if not statement.strip().lower() == 'then':
                    # Create condition block
                    cond_block = self.cfg.create_block(
                        BlockType.IF_CONDITION,
                        f"IF ({condition})",
                        condition=condition
                    )
                    self.cfg.add_edge(current_block.id, cond_block.id)
                    
                    # Create statement block
                    stmt_block = self.cfg.create_block(
                        BlockType.STATEMENT,
                        statement[:50]  # Truncate long statements
                    )
                    stmt_block.statements.append(statement)
                    self.cfg.add_edge(cond_block.id, stmt_block.id)
                    
                    # Create merge block
                    merge_block = self.cfg.create_block(
                        BlockType.STATEMENT,
                        "Continue"
                    )
                    self.cfg.add_edge(stmt_block.id, merge_block.id)
                    self.cfg.add_edge(cond_block.id, merge_block.id)
                    
                    current_block = merge_block
                    
            else:
                # Regular statement
                if current_block.block_type == BlockType.STATEMENT:
                    current_block.statements.append(line_stripped)
                else:
                    # Create a new statement block
                    stmt_block = self.cfg.create_block(
                        BlockType.STATEMENT,
                        line_stripped[:50]  # Truncate long statements
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
        lines = self.source_code.split('\n')
        result = []
        in_procedure = False
        
        # Patterns to match procedure start and end
        proc_start = re.compile(
            rf'^\s*{re.escape(self.procedure_type)}\s+{re.escape(self.procedure_name)}\b',
            re.IGNORECASE
        )
        proc_end = re.compile(
            rf'^\s*end\s+{re.escape(self.procedure_type)}\b',
            re.IGNORECASE
        )
        contains_re = re.compile(r'^\s*contains\s*$', re.IGNORECASE)
        
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
    source_code: str,
    procedure_name: str,
    procedure_type: str
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
