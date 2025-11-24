# -*- coding: utf-8 -*-
#
#  fortran_patterns.py
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
Shared Fortran regex patterns for parsing control flow and other constructs.

This module contains common regex patterns used by both sourceform.py and
control_flow.py to avoid duplication in parsing logic.
"""

import re

# ============================================================================
# Control Flow Statement Patterns
# ============================================================================

# IF-THEN statement with optional label: [label:] IF (condition) THEN
IF_THEN_RE = re.compile(
    r"^\s*(?:(\w+)\s*:)?\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE
)

# ELSE IF statement: ELSE IF (condition) THEN
ELSE_IF_RE = re.compile(r"^\s*else\s*if\s*\((.*?)\)\s*then\s*$", re.IGNORECASE)

# ELSE statement: ELSE
ELSE_RE = re.compile(r"^\s*else\s*$", re.IGNORECASE)

# END IF statement with optional label: END IF [label]
END_IF_RE = re.compile(r"^\s*end\s*if(?:\s+(\w+))?\s*$", re.IGNORECASE)

# DO loop with optional label: [label:] DO control_expression
DO_LOOP_RE = re.compile(r"^\s*(?:(\w+)\s*:)?\s*do\s+(.*)$", re.IGNORECASE)

# END DO statement with optional label: END DO [label]
END_DO_RE = re.compile(r"^\s*end\s*do(?:\s+(\w+))?\s*$", re.IGNORECASE)

# SELECT CASE statement with optional label: [label:] SELECT CASE (expression)
SELECT_CASE_RE = re.compile(
    r"^\s*(?:(\w+)\s*:)?\s*select\s+case\s*\((.*?)\)\s*$", re.IGNORECASE
)

# CASE statement: CASE (value)
CASE_RE = re.compile(r"^\s*case\s*\((.*?)\)\s*$", re.IGNORECASE)

# CASE DEFAULT statement: CASE DEFAULT
CASE_DEFAULT_RE = re.compile(r"^\s*case\s+default\s*$", re.IGNORECASE)

# END SELECT statement with optional label: END SELECT [label]
END_SELECT_RE = re.compile(r"^\s*end\s*select(?:\s+(\w+))?\s*$", re.IGNORECASE)

# Single-line IF statement: IF (condition) statement
SINGLE_IF_RE = re.compile(r"^\s*if\s*\((.*?)\)\s+(.+)$", re.IGNORECASE)

# ============================================================================
# Statement Type Patterns
# ============================================================================

# RETURN statement: RETURN
RETURN_RE = re.compile(r"^\s*return\s*$", re.IGNORECASE)

# USE statement: USE module_name
USE_RE = re.compile(r"^\s*use\s+", re.IGNORECASE)

# IMPLICIT statement: IMPLICIT type
IMPLICIT_RE = re.compile(r"^\s*implicit\s+", re.IGNORECASE)

# Type declaration statement: INTEGER, REAL, etc.
# Matches type declarations including: type(...) and type ::
DECLARATION_RE = re.compile(
    r"^\s*(?:integer|real|double\s+precision|complex|logical|character|class|procedure|type\s*(?:\(|::))",
    re.IGNORECASE,
)


# ============================================================================
# Helper Functions
# ============================================================================


def is_declaration_or_use(line: str) -> bool:
    """Check if a line is a USE, IMPLICIT, or type declaration statement.

    These statements should not appear in the control flow graph as they
    are not part of the execution flow.

    Parameters
    ----------
    line : str
        The stripped line to check

    Returns
    -------
    bool
        True if the line should be skipped in control flow, False otherwise
    """
    return bool(
        USE_RE.match(line) or IMPLICIT_RE.match(line) or DECLARATION_RE.match(line)
    )


def extract_if_condition(line: str) -> str | None:
    """Extract the condition from an IF-THEN statement.

    Parameters
    ----------
    line : str
        The line containing the IF statement

    Returns
    -------
    str or None
        The condition expression, or None if not an IF-THEN statement
    """
    if match := IF_THEN_RE.match(line.strip()):
        # Group 2 contains the condition (group 1 is the optional label)
        return match.group(2)
    return None


def extract_elseif_condition(line: str) -> str | None:
    """Extract the condition from an ELSE IF statement.

    Parameters
    ----------
    line : str
        The line containing the ELSE IF statement

    Returns
    -------
    str or None
        The condition expression, or None if not an ELSE IF statement
    """
    if match := ELSE_IF_RE.match(line.strip()):
        return match.group(1)
    return None


def extract_select_expression(line: str) -> str | None:
    """Extract the expression from a SELECT CASE statement.

    Parameters
    ----------
    line : str
        The line containing the SELECT CASE statement

    Returns
    -------
    str or None
        The select expression, or None if not a SELECT CASE statement
    """
    if match := SELECT_CASE_RE.match(line.strip()):
        # Group 2 contains the expression (group 1 is the optional label)
        return match.group(2)
    return None


def extract_case_value(line: str) -> str | None:
    """Extract the value from a CASE statement.

    Parameters
    ----------
    line : str
        The line containing the CASE statement

    Returns
    -------
    str or None
        The case value, 'DEFAULT' for CASE DEFAULT, or None if not a CASE statement
    """
    line_stripped = line.strip()
    if CASE_DEFAULT_RE.match(line_stripped):
        return "DEFAULT"
    if match := CASE_RE.match(line_stripped):
        return match.group(1)
    return None


def extract_do_control(line: str) -> str | None:
    """Extract the control expression from a DO loop.

    Parameters
    ----------
    line : str
        The line containing the DO statement

    Returns
    -------
    str or None
        The loop control expression, or None if not a DO statement
    """
    if match := DO_LOOP_RE.match(line.strip()):
        # Group 2 contains the control expression (group 1 is the optional label)
        return match.group(2)
    return None
