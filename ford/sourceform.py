# -*- coding: utf-8 -*-
#
#  sourceform.py
#  This file is part of FORD.
#
#  Copyright 2014 Christopher MacMackin <cmacmackin@gmail.com>
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

from __future__ import annotations

from contextlib import suppress
from collections import defaultdict
from dataclasses import dataclass, fields
import re
import os.path
import pathlib
import copy
import textwrap
from typing import (
    cast,
    List,
    Tuple,
    Optional,
    Union,
    Sequence,
    Dict,
    TYPE_CHECKING,
    Iterable,
)
from itertools import chain
from urllib.parse import quote
import sys

import toposort
from pygments import highlight
from pygments.lexers import FortranLexer, FortranFixedLexer, guess_lexer_for_filename
from pygments.formatters import HtmlFormatter

from ford.console import warn
from ford.reader import FortranReader
import ford.utils
from ford.utils import paren_split, strip_paren
from ford.intrinsics import INTRINSICS
from ford._markdown import MetaMarkdown
from ford.settings import ProjectSettings, EntitySettings
from ford._typing import PathLike

import logging
from collections import defaultdict

if TYPE_CHECKING:
    from ford.fortran_project import Project

log = logging.getLogger(__name__)

def extract_base(col: str) -> str:
    """
    Strip off any array‐index or component qualifiers
    so you only get the raw variable name.
    E.g. "aq_ch(iaq)%name"  → "aq_ch"
    """
    # take everything before the first '('
    base = col.split('(', 1)[0]
    # then drop any %component
    return base.split('%', 1)[0]

class IoSession:
    def __init__(self, unit, filename, loop_context=None, line_no=None):
        self.unit = unit
        self.file = filename
        self.operations = []
        self.closed = False
        self.loop_context = loop_context  # e.g., loop variable/name
        self.line_no = line_no            # record line number for context

    def add(self, kind, raw, line_no=None, condition=None):
        """Record an I/O operation with optional line number and condition."""
        self.operations.append({
            "kind": kind,
            "raw": raw.strip(),
            "line": line_no,
            "condition": condition
        })

    def close(self) -> None:
        """Mark the session as closed."""
        self.closed = True

class IoTracker:
    def __init__(self):
        self._open_sessions = {}                # unit → IoSession
        self.completed = defaultdict(list)      # unit → [IoSession,...]
        self.file_mappings = defaultdict(set)   # filename → {unit1, unit2, ...}
        self.stragglers = []                    # IoSessions never closed
        self.condition_stack = []               # Stack of active conditions
        self.current_condition = None           # Current active condition context

    def normalize_file_key(self, fname: str) -> str:
        """
        Collapse any TRIM/ADJUSTL wrappers and '//' concatenations so that
        both
        TRIM(ADJUSTL(in_path_hmd%hmd))//hmd(i)%filename
        and
        hmd(i)%filename
        become simply
        hmd(i)%filename
        """
        if not fname:
            return "<unknown>"
        f = fname.strip().strip('"').strip("'")
        # if string‐concat present, keep only after the last //
        if '//' in f:
            f = f.rsplit('//', 1)[-1].strip()
        # strip single TRIM(...) or ADJUSTL(...) wrapper
        m = re.match(r'^(?:TRIM|ADJUSTL)\((.+)\)$', f, re.IGNORECASE)
        if m:
            return self.normalize_file_key(m.group(1).strip())
        return f    
    
    def push_condition(self, condition_text, line_no=None):
        """Push a new condition context onto the stack."""
        condition_info = {
            'text': condition_text.strip(),
            'line': line_no,
            'type': self._determine_condition_type(condition_text)
        }
        self.condition_stack.append(condition_info)
        self.current_condition = condition_info

    def pop_condition(self):
        """Pop the current condition context from the stack."""
        if self.condition_stack:
            self.condition_stack.pop()
        self.current_condition = self.condition_stack[-1] if self.condition_stack else None

    def _determine_condition_type(self, condition_text):
        """Determine the type of control structure."""
        text_lower = condition_text.lower().strip()
        if text_lower.startswith('if'):
            return 'if'
        elif text_lower.startswith('select case'):
            return 'select'
        elif text_lower.startswith('case'):
            return 'case'
        elif text_lower.startswith('else'):
            return 'else'
        elif text_lower.startswith('do'):
            return 'do'
        return 'unknown'

    def operations_timeline(self) -> dict[str, list[dict]]:
        """
        Returns a dict mapping file or synthetic unit-based name → chronological list of raw I/O operations.
        Used to populate the 'timeline' entry per unit or file.
        """
        result = {}

        for unit, sessions in self.completed.items():  # 🔄 FIXED
            for sess in sessions:
                key = sess.file
                if key == "<unknown>" and sess.unit:
                    key = f"unit_{sess.unit}"
                result.setdefault(key, []).extend(sess.operations)

        return result

    def start(self, unit, filename, line_no=None):
        """Begin a new I/O session, closing any prior one on same unit."""
        if unit in self._open_sessions:
            old = self._open_sessions.pop(unit)
            self.completed[unit].append(old)
        sess = IoSession(unit, filename, line_no=line_no)
        self._open_sessions[unit] = sess
        if filename:
            self.file_mappings[filename].add(unit)

    def record(self, unit, kind, raw, line_no=None):
        """Record a raw I/O operation under the open session for `unit`."""
        sess = self._open_sessions.get(unit)
        if sess:
            sess.add(kind, raw, line_no, condition=self.current_condition)

    def record_or_create(self, unit, kind, raw, line_no=None):
        """
        Record an I/O operation, creating a synthetic session if needed.
        Used for cases like WRITE where the file isn't explicitly opened.
        """
        if unit is None:
            return

        unit = str(unit)
        if unit not in self._open_sessions:
            filename = f"unit_{unit}"
            sess = IoSession(unit=unit, filename=filename, line_no=line_no)
            self._open_sessions[unit] = sess
        else:
            sess = self._open_sessions[unit]

        sess.add(kind, raw, line_no, condition=self.current_condition)

    def close(self, unit, line_no=None):
        """Close and archive the I/O session for `unit`."""
        sess = self._open_sessions.pop(unit, None)
        if sess:
            sess.add('close', f'close({unit})', line_no, condition=self.current_condition)
            sess.close()
            self.completed[unit].append(sess)

    def finalize(self) -> None:
        """Archive any unclosed sessions as stragglers."""
        self.stragglers = list(self._open_sessions.values())
        if self.stragglers:
            log.warning("Unclosed IO sessions: %s", [(s.unit, s.file) for s in self.stragglers])
        for unit, sess in list(self._open_sessions.items()):
            self.completed[unit].append(sess)
        self._open_sessions.clear()

    def report(self) -> None:
        """Print full I/O report for debugging."""
        for unit, sessions in self.completed.items():
            for sess in sessions:
                status = 'closed' if sess.closed else 'unclosed'


    def get_io_summary(self) -> dict:
        """Return concise counts per unit and global op counts."""
        summary = {'units': {}, 'files': {}, 'operations': {}}
        for unit, sessions in self.completed.items():
            counts = defaultdict(int)
            files = set()
            for sess in sessions:
                files.add(sess.file)
                for op in sess.operations:
                    counts[op['kind']] += 1
                    summary['operations'].setdefault(op['kind'], 0)
                    summary['operations'][op['kind']] += 1
            summary['units'][unit] = {'files': list(files), 'counts': dict(counts)}
        for fname, units in self.file_mappings.items():
            if fname:
                summary['files'][fname] = {'units': list(units), 'count': len(units)}
        return summary

    def summarize_file_io(self) -> dict[str, dict]:
        """
        Produce both:
        - a structured I/O summary per file:
            - headers:        titldum/header reads
            - index_reads:    single-column 'i' reads
            - data_reads:     grouped reads by columns
            - header_writes:  single-column titldum/header writes
            - data_writes:    grouped writes by columns
        - a full raw I/O timeline per file
        """
        raw_result: dict[str, dict] = {}

        for sessions in self.completed.values():
            for sess in sessions:
                fname = self.normalize_file_key(sess.file)
                if fname == "<unknown>" and sess.unit:
                    fname = f"unit_{sess.unit}"
                rec = raw_result.setdefault(fname, {
                    "unit":           sess.unit,
                    "headers":        [],
                    "index_reads":    [],
                    "data_reads":     [],
                    "header_writes":  [],
                    "data_writes":    []
                })

                for op in sess.operations:
                    kind = op["kind"].lower()
                    if kind not in ("read", "write"):
                        continue

                    raw_line = op["raw"]

                    # --- Robustly extract the part after write(...) or read(...)
                    paren_level = 0
                    end_idx = None
                    for idx, ch in enumerate(raw_line):
                        if ch == '(':
                            paren_level += 1
                        elif ch == ')':
                            paren_level -= 1
                            if paren_level == 0:
                                end_idx = idx
                                break
                    if end_idx is None or end_idx + 1 >= len(raw_line):
                        continue  # malformed

                    cols_part = raw_line[end_idx + 1:].strip()

                    # --- Split on top-level commas (ignoring nested parentheses)
                    cols, buf, depth = [], "", 0
                    for ch in cols_part:
                        if ch == "(":
                            depth += 1; buf += ch
                        elif ch == ")" and depth > 0:
                            depth -= 1; buf += ch
                        elif ch == "," and depth == 0:
                            cols.append(buf.strip()); buf = ""
                        else:
                            buf += ch
                    if buf.strip():
                        cols.append(buf.strip())

                    # --- Strip one layer of parens from each col
                    clean_cols = []
                    for c in cols:
                        c2 = c.strip()
                        if c2.startswith("(") and c2.endswith(")"):
                            c2 = c2[1:-1].strip()
                        clean_cols.append(c2)

                    # === Classification ===
                    if kind == "read":
                        if len(clean_cols) == 1:
                            single = clean_cols[0]
                            if single == "i":
                                if single not in rec["index_reads"]:
                                    rec["index_reads"].append(single)
                            elif single in ("titldum", "header"):
                                if single not in rec["headers"]:
                                    rec["headers"].append(single)
                            elif "(" in single or "%" in single:
                                rec["data_reads"].append((single,))
                            else:
                                if single not in rec["headers"]:
                                    rec["headers"].append(single)
                        else:
                            rec["data_reads"].append(tuple(clean_cols))

                    elif kind == "write":
                        if len(clean_cols) == 1 and clean_cols[0] in ("titldum", "header"):
                            if clean_cols[0] not in rec["header_writes"]:
                                rec["header_writes"].append(clean_cols[0])
                        else:
                            rec["data_writes"].append(tuple(clean_cols))

        # Step 2: Collapse duplicate reads and writes
        final_result = {}

        for fname, rec in raw_result.items():
            # collapse data_reads
            dr_counts: dict[tuple[str, ...], int] = defaultdict(int)
            for cols in rec["data_reads"]:
                dr_counts[cols] += 1
            rec["data_reads"] = [
                {"columns": list(cols), "rows": count}
                for cols, count in dr_counts.items()
            ]

            # collapse data_writes
            dw_counts: dict[tuple[str, ...], int] = defaultdict(int)
            for cols in rec["data_writes"]:
                dw_counts[cols] += 1
            rec["data_writes"] = [
                {"columns": list(cols), "rows": count}
                for cols, count in dw_counts.items()
            ]

            # attach timeline
            timeline = self.operations_timeline().get(fname, [])
            all_timelines = self.operations_timeline()
            log.debug("Available timeline keys: %s", list(all_timelines.keys()))
            log.debug("Available ops for key %s: %s", fname, all_timelines.get(fname, []))

            final_result[fname] = {
                "summary": rec,
                "timeline": timeline
            }

        return final_result




VAR_TYPE_STRING = r"^integer|real|double\s*precision|character|complex|double\s*complex|logical|type|class|procedure|enumerator"
VARKIND_RE = re.compile(r"\((.*)\)|\*\s*(\d+|\(.*\))")
KIND_RE = re.compile(r"kind\s*=\s*([^,\s]+)", re.IGNORECASE)
KIND_SUFFIX_RE = re.compile(r"(?P<initial>.*)_(?P<kind>[a-z]\w*)", re.IGNORECASE)
CHAR_KIND_SUFFIX_RE = re.compile(r"(?P<kind>[a-z]\w*)_(?P<initial>.*)", re.IGNORECASE)
LEN_RE = re.compile(r"(?:len\s*=\s*(\w+|\*|:|\d+)|(\d+))", re.IGNORECASE)
ATTRIBSPLIT_RE = re.compile(r",\s*(\w.*?)::\s*(.*)\s*")
ATTRIBSPLIT2_RE = re.compile(r"\s*(::)?\s*(.*)\s*")
ASSIGN_RE = re.compile(r"(\w+\s*(?:\([^=]*\)))\s*=(?!>)(?:\s*([^\s]+))?")
POINT_RE = re.compile(r"(\w+\s*(?:\([^=>]*\)))\s*=>(?:\s*([^\s]+))?")
EXTENDS_RE = re.compile(r"extends\s*\(\s*(?P<base>[^()\s]+)\s*\)", re.IGNORECASE)
DOUBLE_PREC_RE = re.compile(r"double\s+precision", re.IGNORECASE)
DOUBLE_CMPLX_RE = re.compile(r"double\s+complex", re.IGNORECASE)
QUOTES_RE = re.compile(r"\"([^\"]|\"\")*\"|'([^']|'')*'", re.IGNORECASE)
PARA_CAPTURE_RE = re.compile(r"<p>.*?</p>", re.IGNORECASE | re.DOTALL)
COMMA_RE = re.compile(r",(?!\s)")
NBSP_RE = re.compile(r" (?= )|(?<= ) ")
DIM_RE = re.compile(r"^\w+\s*(\(.*\))\s*$")
PROTO_RE = re.compile(r"(\*|\w+)\s*(?:\((.*)\))?")
CALL_AND_WHITESPACE_RE = re.compile(r"\(\)|\s")

base_url = ""


SUBLINK_TYPES = {
    "variable": "variables",
    "type": "types",
    "constructor": "constructor",
    "interface": "interfaces",
    "absinterface": "absinterfaces",
    "subroutine": "subroutines",
    "function": "functions",
    "final": "finalprocs",
    "bound": "boundprocs",
    "modproc": "modprocs",
    "common": "common",
}


def _find_in_list(collection: Iterable, name: str) -> Optional[FortranBase]:
    for item in collection:
        # `item` might still be a string if we've not managed to
        # correlate it for whatever reason, if so skip it
        if not isinstance(item, FortranBase):
            continue
        if name.lower() == item.name.lower():
            return item
    return None


def read_docstring(source: FortranReader, docmark: str) -> List[str]:
    """Read a contiguous docstring"""
    docstring: List[str] = []
    docmark_str = f"!{docmark}"
    length = len(docmark_str)

    # if source isn’t really iterable (e.g. a FortranSourceFile), bail out
    if not hasattr(source, "__next__"):
        return docstring

    try:
        # consume leading doc-comment lines
        while True:
            line = next(source)
            if line.startswith(docmark_str):
                docstring.append(line[length:])
            else:
                source.pass_back(line)
                break
    except StopIteration:
        # ran off EOF—just return whatever we got
        pass
    except TypeError:
        # source wasn’t iterable after all
        return []

    return docstring


class Associations:
    """
    A class for storing associations. Associations are added and removed in batches, akin
    to how they are added, and fall out of scope in Fortran ASSOCIATE blocks.
    """

    def __init__(self) -> None:
        # a list of dictionaries representing the associations in each batch, in order of
        # when the batch was added
        self._batches: List[Dict[str, List[str]]] = []

    def add_batch(self, associations: List[str]):
        """
        adds a batch of associations to the associations dictionary
        """
        current_batch = {}
        for item in associations:
            # parse the association
            new, old = item.split("=>")
            new = new.strip().lower()
            current_batch[new] = (
                old.lower().replace("()", "").replace(" ", "").split("%")
            )
            # apply associations to this association if they exist
            if current_batch[new][0] in self:
                current_batch[new][0:1] = self[current_batch[new][0]]
        self._batches.append(current_batch)

    def remove_last_batch(self):
        """
        removes the last batch of associations
        """
        if not self._batches:
            raise IndexError("No batches to remove")
        self._batches.pop()

    def __getitem__(self, key: str) -> List[str]:
        for batch in reversed(self._batches):
            if key in batch:
                return batch[key]
        raise KeyError(key)

    def __contains__(self, key):
        for batch in reversed(self._batches):
            if key in batch:
                return True
        return False


class FortranBase:
    """
    An object containing the data common to all of the classes used to represent
    Fortran data.
    """

    POINTS_TO_RE = re.compile(r"\s*=>\s*", re.IGNORECASE)
    SPLIT_RE     = re.compile(r"\s*,\s*", re.IGNORECASE)

    IS_SPOOF = False
    # … your existing class‐level regexes and mappings …

    def __init__(
        self,
        source: FortranReader,
        first_line: re.Match,
        parent: Optional[FortranContainer] = None,
        inherited_permission: str = "public",
        strings: Optional[List[str]] = None,
        line_number: int = None,
    ):
        # start an I/O session tracker for this code unit
        self.io_tracker = IoTracker()

        # Record starting line number
        if line_number is not None:
            self.line_number = line_number
        else:
            self.line_number = getattr(source, "line_number", None)

        self.name = "unknown"
        self.visible = False
        self.permission = inherited_permission.lower()
        self.strings: List[str] = strings or []

        self.obj = type(self).__name__[7:].lower()
        if self.obj in ["subroutine", "function", "moduleprocedureimplementation"]:
            self.obj = "proc"

        self.parent = parent
        if self.parent:
            self.parobj: Optional[str] = self.parent.obj
            self.display: List[str] = self.parent.display
            self.settings: ProjectSettings = self.parent.settings
        else:
            self.parobj = None
            self.display = []
            self.settings = ProjectSettings()

        self.base_url = pathlib.Path(self.settings.project_url)
        try:
            self.doc_list = read_docstring(source, self.settings.docmark)
        except TypeError:
            # source isn’t iterable (e.g. a FortranSourceFile), so no docstring to read
            self.doc_list = []
        self.hierarchy = self._make_hierarchy()
        self.read_metadata()

        # Some entities are reachable from more than one parent …
        self.source_file._to_be_markdowned.append(self)

        # only initialize if we have a real regex match
        if first_line:
            self._initialize(first_line)
        del self.strings

    def _make_hierarchy(self) -> List[FortranContainer]:
        """Create list of ancestor entities"""
        hierarchy = []
        # This is a bit gross, but shuts mypy up
        cur: Optional[FortranBase] = self
        while cur := getattr(cur, "parent", None):
            hierarchy.append(cur)
        hierarchy.reverse()
        return hierarchy

    def _initialize(self, line: re.Match) -> None:
        raise NotImplementedError()

    @property
    def source_file(self) -> FortranSourceFile:
        """Source file containing this entity"""
        # If `hierarchy` is empty, it's probably because it's a source file
        return cast(FortranSourceFile, (self.hierarchy[0] if self.hierarchy else self))

    @property
    def filename(self) -> str:
        """Name of the file containing this entity"""
        return self.source_file.name

    def get_dir(self) -> Optional[str]:
        if isinstance(
            self,
            (
                FortranSourceFile,
                FortranProgram,
                FortranModule,
                GenericSource,
                FortranBlockData,
                FortranNamelist,
            ),
        ) or (
            isinstance(
                self,
                (
                    FortranType,
                    FortranInterface,
                    FortranProcedure,
                    FortranModuleProcedureImplementation,
                ),
            )
            and isinstance(
                self.parent,
                (
                    FortranSourceFile,
                    FortranProgram,
                    FortranModule,
                    FortranSubmodule,
                    FortranBlockData,
                ),
            )
        ):
            return self.obj

        return None

    def get_url(self) -> Optional[str]:
        """URL of this entity, relative to base URL"""

        if hasattr(self, "external_url"):
            return self.external_url

        if loc := self.get_dir():
            return f"{loc}/{self.ident}.html"

        if (
            isinstance(
                self,
                (
                    FortranBoundProcedure,
                    FortranCommon,
                    FortranVariable,
                    FortranEnum,
                    FortranFinalProc,
                    FortranProcedure,
                ),
            )
            and self.parent is not None
        ):
            if parent_url := self.parent.get_url():
                if "#" in parent_url:
                    parent_url, _ = parent_url.split("#")
                return f"{parent_url}#{self.anchor}"
            return None
        return None

    @property
    def full_url(self) -> Optional[str]:
        """URL of this entity, including the base URL"""
        if hasattr(self, "external_url"):
            return self.external_url

        if (url := self.get_url()) is not None:
            return str(self.base_url / url)

        return None

    def lines_description(self, total, total_all=0, obj=None):
        if not obj:
            obj = self.obj
        total = total or self.num_lines
        # Fallback if pretty_obj is missing
        pretty_obj = getattr(self, 'pretty_obj', None)
        if pretty_obj and obj in pretty_obj:
            obj_name = pretty_obj[obj]
        else:
            obj_name = str(obj)
        description = f"{float(self.num_lines) / total * 100:4.1f}% of total for {obj_name}."
        if total_all:
            description = (
                f"<p>{description}</p>Including implementation: {self.num_lines_all} statements, "
                f"{float(self.num_lines_all) / total_all * 100:4.1f}% of total for {obj_name}."
            )
        return description

    @property
    def ident(self) -> str:
        """Return a unique identifier for this object"""
        return namelist.get_name(self)

    @property
    def anchor(self) -> str:
        """Return a string suitable for an HTML anchor link"""
        return f"{self.obj}-{quote(self.ident)}"

    def __str__(self):
        if (url := self.full_url) and getattr(self, "visible", True):
            name = self.name or "<em>unnamed</em>"
            return f"<a href='{url}'>{name}</a>"
        return self.name or ""

    def __lt__(self, other):
        """
        Compare two Fortran objects. Needed to make toposort work.
        """
        return self.ident < other.ident

    def _set_display(self):
        if self.parent:
            self.display = self.parent.display

        tmp = [item.lower() for item in self.meta.display]
        if isinstance(self, FortranSourceFile):
            while "none" in tmp:
                tmp.remove("none")

        if not tmp:
            return

        if "none" in tmp:
            self.display = []
        elif "public" not in tmp and "private" not in tmp and "protected" not in tmp:
            return
        else:
            self.display = tmp

    def read_metadata(self):
        """Read the metadata from an entity's docstring"""

        self.meta = EntitySettings.from_project_settings(self.settings)

        if len(self.doc_list) > 0:
            if len(self.doc_list) == 1 and ":" in self.doc_list[0]:
                words = self.doc_list[0].split(":")[0].strip()
                field_names = [field.name for field in fields(EntitySettings)]
                if words.lower() not in field_names:
                    self.doc_list.insert(0, "")

            meta, self.doc_list = ford.utils.meta_preprocessor(self.doc_list)
            self.meta.update(meta, f"{self.filename}:{self.name}")
        else:
            if self.settings.warn and self.obj not in ("sourcefile", "genericsource"):
                # TODO: Add ability to print line number where this item is in file
                warn(f"Undocumented {self.obj} '{self.name}' in file '{self.filename}'")

        self._set_display()

    def markdown(self, md: MetaMarkdown):
        """
        Process the documentation with Markdown to produce HTML.
        """

        if hasattr(self, "num_lines"):
            self.meta.num_lines = self.num_lines

        # Remove any common leading whitespace from the docstring
        # so that the markdown conversion is a bit more robust
        try:
            self.doc = md.reset().convert(
                textwrap.dedent("\n".join(self.doc_list)), context=self
            )
        except (RuntimeError, ValueError) as e:
            raise ValueError(
                f"Error when rendering docstring for {self.obj} '{self.name}' in '{self.filename}':\n    {e}"
            )

        if self.meta.summary is not None:
            self.meta.summary = md.convert(" ".join(self.meta.summary.split()), context=self)
        elif paragraph := PARA_CAPTURE_RE.search(self.doc):
            # If there is no stand-alone webpage for this item, e.g.
            # an internal routine, make the whole doc blob appear,
            # without the link to "more..."
            self.meta.summary = paragraph.group() if self.get_url() else self.doc
        else:
            self.meta.summary = ""

        if self.meta.summary.strip() != self.doc.strip():
            self.meta.summary += f'<a href="../{self.get_url()}" class="pull-right"><emph>Read more&hellip;</emph></a>'

        if self.obj in ["proc", "type", "program"] and self.meta.source:
            obj = getattr(self, "proctype", self.obj).lower()
            regex = re.compile(
                rf"""
                ^(?:[\w(),*: \t]*?)?         # Attributes, function type
                \b{obj}\b                    # Subroutine/function
                (?:[\w(),*: \t]+?)?[ \t]+    # Interstitial nonsense
                \b{self.name}\b[ \t\n,(].*?  # Entity name
                ^[ \t]*\bend[ \t]*{obj}\b[ \t]+\b{self.name}\b[ \t]*? # End statement
                (?:!.*?)?$
                """,
                re.IGNORECASE | re.DOTALL | re.MULTILINE | re.VERBOSE,
            )
            if match := regex.search(self.source_file.raw_src):
                self.src = highlight(
                    match.group(),
                    FortranLexer(),
                    HtmlFormatter(cssclass="hl codehilite"),
                )
            else:
                self.src = ""
                if self.settings.warn:
                    warn(
                        f"Could not extract source code for {self.obj} '{self.name}' in file '{self.filename}'"
                    )
        # Add I/O information to metadata if available
        if hasattr(self, 'io_tracker') and isinstance(self, (FortranProcedure, FortranProgram, FortranModule)):
            io_summary = self.io_tracker.get_io_summary()
            total_ops = io_summary["operations"].get("total", 0)
            if total_ops > 0:
                self.meta.io_summary = io_summary

                # Generate I/O documentation section
                if io_summary["files"]:
                    io_doc = "<h3>File I/O</h3><ul>"
                    for filename, file_info in io_summary["files"].items():
                        io_doc += f"<li><strong>{filename}</strong>: accessed via {len(file_info['units'])} unit(s)</li>"
                    io_doc += "</ul>"

                    if io_summary["operations"].get("read", 0) > 0 or io_summary["operations"].get("write", 0) > 0:
                        io_doc += "<h4>I/O Operations</h4><ul>"
                        if io_summary["operations"]["read"] > 0:
                            io_doc += f"<li>Read operations: {io_summary['operations']['read']}</li>"
                        if io_summary["operations"]["write"] > 0:
                            io_doc += f"<li>Write operations: {io_summary['operations']['write']}</li>"
                        io_doc += "</ul>"

                    # Append to documentation
                    self.doc += io_doc

    def sort_components(self) -> None:
        """Sorts components using the method specified in the object
        meta/project settings

        """

        def permission(item):
            permission_type = getattr(item, "permission", "default")
            sorting = {"default": 0, "public": 1, "protected": 2, "private": 3}
            return sorting[permission_type]

        def fortran_type_name(item):
            if item.obj == "variable":
                retstr = item.vartype
                if retstr == "class":
                    retstr = "type"
                if item.kind:
                    retstr += f"-{item.kind}"
                if item.strlen:
                    retstr += f"-{item.strlen}"
                if item.proto:
                    retstr += f"-{item.proto[0]}"
                return retstr
            if item.obj == "proc":
                return_var = (
                    f"-{fortran_type_name(item.retvar)}"
                    if item.proctype == "Function"
                    else ""
                )
                return f"{item.proctype.lower()}{return_var}"

            return item.obj

        SORT_KEY_FUNCTIONS = {
            "alpha": lambda item: item.name,
            "permission": permission,
            "permission-alpha": lambda item: f"{permission(item)}-{item.name}",
            "type": fortran_type_name,
            "type-alpha": lambda item: f"{fortran_type_name(item)}-{item.name}",
            "src": None,
        }

        sort_key = SORT_KEY_FUNCTIONS[self.settings.sort.lower()]
        if sort_key is None:
            return

        for entities in [
            "variables",
            "modules",
            "submodules",
            "common",
            "subroutines",
            "modprocedures",
            "functions",
            "interfaces",
            "absinterfaces",
            "types",
            "programs",
            "blockdata",
            "boundprocs",
            "finalprocs",
        ]:
            entity = getattr(self, entities, [])
            entity.sort(key=sort_key)

    @property
    def routines(self):
        """Iterator returning all procedures"""
        return self.iterator("functions", "subroutines", "modprocedures")

    def iterator(self, *argv):
        """Iterator returning any list of elements via attribute lookup in ``self``

        This iterator retains the order of the arguments"""
        for arg in argv:
            if hasattr(self, arg):
                for item in getattr(self, arg):
                    yield item

    @property
    def children(self):
        """Iterator over all child entities"""

        non_list_children = ["constructor", "procedure", "retvar"]

        return chain(
            self.iterator(
                "absinterfaces",
                "args",
                "blockdata",
                "bindings",
                "boundprocs",
                "common",
                "enums",
                "functions",
                "modprocedures",
                "modules",
                "namelists",
                "programs",
                "submodules",
                "subroutines",
                "types",
                "variables",
                # Non-alphabetical order to preserve previous behaviour of
                # finding types before interfaces
                "interfaces",
                "finalprocs",
            ),
            filter(None, (getattr(self, item, None) for item in non_list_children)),
        )

    def find_child(
        self, name: str, entity: Optional[str] = None
    ) -> Optional[FortranBase]:
        """Find a child of this entity by name

        Parameters
        ----------
        name : str
            Name of child to look up
        entity : Optional[str]
            The class of entity (module, function, and so on)

        Returns
        -------
        Optional[FortranBase]
            Child if found, `None` if not

        """

        if entity is not None:
            try:
                collection_name = SUBLINK_TYPES[entity.lower()]
            except KeyError:
                raise ValueError(f"Unknown class of entity {entity!r}")
            if not hasattr(self, collection_name):
                raise ValueError(f"{self.obj!r} cannot have child {entity!r}")
            # Ensure this is a list, as constructors are single items
            collection = list(getattr(self, collection_name))
        else:
            collection = self.children

        return _find_in_list(collection, name)

    def _should_display(self, item) -> bool:
        """Return True if item should be displayed"""
        if self.settings.hide_undoc and not item.doc_list:
            return False
        return item.permission in self.display

    def filter_display(self, collection: Sequence) -> List:
        """Remove items from collection if they shouldn't be displayed"""

        return [obj for obj in collection if self._should_display(obj)]


class FortranContainer(FortranBase):
    """
    A class on which any classes requiring further parsing are based.
    """

    ATTRIB_RE = re.compile(
        r"^(asynchronous|allocatable|bind\s*\(.*\)|data|dimension|external|intent\s*\(\s*\w+\s*\)|optional|parameter|"
        r"pointer|private|protected|public|save|target|value|volatile)(?:\s+|\s*::\s*)((/|\(|\w).*?)\s*$",
        re.IGNORECASE,
    )
    END_RE = re.compile(
        r"^end\s*(?:(module|submodule|subroutine|function|procedure|program|type|interface|enum|block\sdata|block|associate)(?:\s+(\w.*))?)?$",
        re.IGNORECASE,
    )
    BLOCK_RE = re.compile(r"^(\w+\s*:)?\s*block\s*$", re.IGNORECASE)
    BLOCK_DATA_RE = re.compile(r"^block\s*data\s*(\w+)?\s*$", re.IGNORECASE)
    ASSOCIATE_RE = re.compile(
        r"""^(\w+\s*:)?         # Optional label
        \s*associate\s*\(       # Required associate statement
        (?P<associations>.+)    # Associations
        \)\s*$""",
        re.IGNORECASE | re.VERBOSE,
    )
    ENUM_RE = re.compile(r"^enum\s*,\s*bind\s*\(.*\)\s*$", re.IGNORECASE)
    MODPROC_RE = re.compile(
        r"^(?P<module>module\s+)?procedure\s*(?:::|\s)\s*(?P<names>\w.*)$",
        re.IGNORECASE,
    )
    MODULE_RE = re.compile(r"^module(?:\s+(?P<name>\w+))?$", re.IGNORECASE)
    SUBMODULE_RE = re.compile(
        r"""^submodule\s*
        \(\s*(?P<ancestor_module>\w+)\s*         # Non-optional ancestor module
        (?::\s*(?P<parent_submod>\w+))?\s*\)  # Optional parent submodule
        \s*(?P<name>\w+)                      # This submodule's name
        $""",
        re.IGNORECASE | re.VERBOSE,
    )
    PROGRAM_RE = re.compile(r"^program(?:\s+(\w+))?$", re.IGNORECASE)
    SUBROUTINE_RE = re.compile(
        r"""^\s*(?:(?P<attributes>.+?)\s+)?     # Optional attributes
        subroutine\s+(?P<name>\w+)\s*           # Required subroutine name
        (?P<arguments>\([^()]*\))?              # Optional arguments
        (?:\s*bind\s*\(\s*(?P<bindC>.*)\s*\))?$ # Optional C-binding""",
        re.IGNORECASE | re.VERBOSE,
    )
    FUNCTION_RE = re.compile(
        r"""^(?:(?P<attributes>.+?)\s*)?               # Optional attributes (including type)
        function\s+(?P<name>\w+)\s*                    # Required function name
        (?P<arguments>\([^()]*\))?                     # Required arguments
        (?=(?:.*result\s*\(\s*(?P<result>\w+)\s*\))?)  # Optional result name
        (?=(?:.*bind\s*\(\s*(?P<bindC>.*)\s*\))?).*$   # Optional C-binding""",
        re.IGNORECASE | re.VERBOSE,
    )
    TYPE_RE = re.compile(
        r"^type(?:\s+|\s*(,.*)?::\s*)((?!(?:is\s*\())\w+)\s*(\([^()]*\))?\s*$",
        re.IGNORECASE,
    )
    INTERFACE_RE = re.compile(r"^(abstract\s+)?interface(?:\s+(.+))?$", re.IGNORECASE)
    BOUNDPROC_RE = re.compile(
        r"""^(?P<generic>generic|procedure)\s*  # Required keyword
        (?P<prototype>\([^()]*\))?\s*           # Optional interface name
        (?:,\s*(?P<attributes>\w[^:]*))?        # Optional list of attributes
        (?:\s*::)?\s*                           # Optional double-colon
        (?P<names>\w.*)$                        # Required name(s)
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    COMMON_RE = re.compile(r"^common(?:\s*/\s*(\w+)\s*/\s*|\s+)(\w+.*)", re.IGNORECASE)
    COMMON_SPLIT_RE = re.compile(r"\s*(/\s*\w+\s*/)\s*", re.IGNORECASE)
    FINAL_RE = re.compile(r"^final\s*::\s*(\w.*)", re.IGNORECASE)
    USE_RE = re.compile(
        r"^use(?:\s*(?:,\s*(?:non_)?intrinsic\s*)?::\s*|\s+)(\w+)\s*($|,.*)",
        re.IGNORECASE,
    )
    ARITH_GOTO_RE = re.compile(r"go\s*to\s*\([0-9,\s]+\)", re.IGNORECASE)
    CALL_RE = re.compile(
        r"""(?P<call_chain>
                (?:(?:\s*\w+\s*(?:\(\))?\s*%\s*)+)? # Optional type component access
                (?:\w+\s*\(.*?\))                   # Required function name
            )
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    SUBCALL_RE = re.compile(
        r"""
        ^(?:if\s*\(.*\)\s*)?    # Optional 'if' statement
        call\s+                 # Required keyword
        (?P<call_chain>
            (?:.*%\s*)?         # Optional type component access
            (?:\w+\s*(?:\(\))?) # Required subroutine name
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    FORMAT_RE = re.compile(r"^[0-9]+\s+format\s+\(.*\)", re.IGNORECASE)

    VARIABLE_STRING = (
        r"^(integer|real|double\s*precision|character|complex|double\s*complex|logical|type(?!\s+is)|class(?!\s+is|\s+default)|"
        r"procedure|enumerator{})\s*((?:\(|\s\w|[:,*]).*)$"
    )
    NAMELIST_RE = re.compile(
        r"namelist\s*/(?P<name>\w+)/\s*(?P<vars>(?:\w+,?\s*)+)", re.IGNORECASE
    )
    ASSIGNMENT_RE = re.compile(
        r"^\s*(?P<lhs>(?:\w+%)*\w+)\s*=\s*(?P<rhs>.+)$",
        re.IGNORECASE | re.VERBOSE,
    )

    IO_VAR_STATEMENT_RE = re.compile(
        r"""^\s*
            (?P<io_stmt>inquire|open|write)            # Fortran I/O statement
            \s*\(                                      # Opening parenthesis
            (?P<arguments>.*?)\)                       # Arguments inside parentheses
            \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    MEMBER_ACCESS_RE = re.compile(
        r"\w+(?:\(\))?(?:%\w+(?:\(\))?)+",  # Match items containing % explicitly
        re.IGNORECASE,
    )

    NUMBER_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")

    # Better regex that handles both cases: (108) and (108, ...)
    IO_UNIT_RE = re.compile(r'\(\s*(?P<unit>[^,)\s]+)(?:\s*,|\s*\))')

    # pull recl if present anywhere
    RECL_RE = re.compile(r'recl\s*=\s*(\d+)', re.IGNORECASE)
    TRIM_ADJUST_RE = re.compile(r'^(?:\s*(?:trim|adjustl))\s*\(\s*(.+)\s*\)\s*$',
                                re.IGNORECASE)


    def __init__(
        self, source, first_line, parent=None, inherited_permission="public", strings=[]
    ):
        self.num_lines = 0
        if not isinstance(self, FortranSourceFile):
            self.num_lines += 1
        if type(self) != FortranSourceFile:
            FortranBase.__init__(
                self, source, first_line, parent, inherited_permission, strings
            )
        incontains = False
        if type(self) is FortranSubmodule:
            self.permission = "private"

        typestr = ""
        for vtype in self.settings.extra_vartypes:
            typestr = typestr + "|" + vtype
        self.VARIABLE_RE = re.compile(
            self.VARIABLE_STRING.format(typestr), re.IGNORECASE
        )

        # Initialize the new attribute to store variable assignments

        self.member_access_results = []  # For `%`-based member access
        self.other_results = []  # For non-member-access items
        self.type_results = {} # For type definitions

        self.var_ug = {} # For procedures
        self.var_ug_na = [] # For procedures
        self.var_ug_local = {} # For procedures
        self.io_lines = []
        self.fvar = {}
        self.pjson = {}
        self.io_json = {}


        # Define a set of symbols to exclude
        self.symbols = {"*", "<", ">", "=", ":", ".", ",","/","-","+", '**'}
        # Fortran Control Structures
        self.fortran_control = {
            "if", "then", "do", "select", "case", "end", "cycle", "stop", "continue", "goto", "else",
            "implicit", "call", "return", "exit", "enddo", "endif", 'while', 'elseif'
        }

        # Fortran Operators
        self.fortran_operators = {
            ".or.", ".and.", ".not.", "=", "<", ">", "0:0"
        }

        # Fortran Intrinsic Functions
        self.fortran_intrinsics = {
            "abs", "acos", "asin", "atan", "exp", "log", "log10", "mod", "sin", "cos",
            "tan", "sqrt", "min", "max", "amin1", "amax1", "Sqrt", "alog", "alog10"
        }

        # Fortran Reserved Words
        self.fortran_reserved = {
            "allocate", "deallocate",
             "source",  "kind", "len", "size", "allocated", "associated",
            "null", "none", "true", "false"
        }

        #Fortran IO Words
        self.fortran_io = {
            "read", "write", "print", "format", "unit", "rewind", "backspace", "endfile",
            "inquire", "open", "close", "flush", "file", "exist", "iostat"
        }

        # Custom Keywords
        self.fortran_custom = {
            "-Theta", "Theta", "Max", "Min", "Exp", "float", "int"
        }


        # This is a little bit confusing, because `permission` here is sort of
        # overloaded for "permission for this entity", and "permission for child
        # entities". For example, the former doesn't apply to modules or programs,
        # while for procedures _only_ the first applies. For things like types, we
        # need to keep track of these meanings separately. Also note that
        # `child_permission` for types can be different for components and bound
        # procedures, but luckily they cannot be mixed in the source, so we don't
        # need to actually track `child_permission` separately for them both
        child_permission = (
            "public" if isinstance(self, FortranType) else self.permission
        )

        blocklevel = 0
        associations = Associations()

        for line in source:
            # grab the current line number from the FortranReader
            lineno = getattr(source, "line_number", None)
            if line[0:2] == "!" + self.settings.docmark:
                self.doc_list.append(line[2:])
                continue
            if line.strip() != "":
                self.num_lines += 1

            # Temporarily replace all strings to make the parsing simpler
            self.strings = []
            search_from = 0
            while quote := QUOTES_RE.search(line[search_from:]):
                self.strings.append(quote.group())
                line = line[0:search_from] + QUOTES_RE.sub(
                    f'"{len(self.strings) - 1}"', line[search_from:], count=1
                )
                search_from += QUOTES_RE.search(line[search_from:]).end(0)

            # Cache the lowercased line
            line_lower = line.lower()

            if self.settings.lower:
                line = line_lower

            # Check the various possibilities for what is on this line
            if line_lower == "contains":
                if not incontains and isinstance(self, _can_have_contains):
                    incontains = True
                    if isinstance(self, FortranType):
                        child_permission = "public"
                elif incontains:
                    self.print_error(line, "Multiple CONTAINS statements present")
                else:
                    self.print_error(line, "Unexpected CONTAINS statement")
            elif line_lower in ["public", "private", "protected"]:
                child_permission = line_lower
                if not isinstance(self, FortranType):
                    self.permission = line_lower
            elif line_lower == "sequence":
                if type(self) == FortranType:
                    self.sequence = True
            elif self.FORMAT_RE.match(line):
                # There's nothing interesting for us in a format statement
                continue
            elif (match := self.ATTRIB_RE.match(line)) and blocklevel == 0:
                attr = match.group(1).lower().replace(" ", "")
                if len(attr) >= 4 and attr[0:4].lower() == "bind":
                    attr = attr.replace(",", ", ")
                if hasattr(self, "attr_dict"):
                    if attr == "data":
                        pass
                    elif attr in ["dimension", "allocatable", "pointer"]:
                        names = ford.utils.paren_split(",", match.group(2))
                        for name in names:
                            name = name.strip().lower()
                            try:
                                open_parenthesis = name.index("(")
                                var_name = name[:open_parenthesis]
                                dimensions = name[open_parenthesis:]
                            except ValueError:
                                var_name = name
                                dimensions = ""

                            self.attr_dict[var_name].append(attr + dimensions)
                    else:
                        stmnt = match.group(2)
                        if attr == "parameter":
                            stmnt = stmnt[1:-1].strip()
                        names = ford.utils.paren_split(",", stmnt)
                        search_from = 0
                        while QUOTES_RE.search(attr[search_from:]):
                            num = int(
                                QUOTES_RE.search(attr[search_from:]).group()[1:-1]
                            )
                            attr = attr[0:search_from] + QUOTES_RE.sub(
                                self.strings[num], attr[search_from:], count=1
                            )
                            search_from += QUOTES_RE.search(attr[search_from:]).end(0)
                        for name in names:
                            if attr == "parameter":
                                split = ford.utils.paren_split("=", name)
                                name = split[0].strip().lower()
                                self.param_dict[name] = split[1]
                            name = name.strip().lower()
                            self.attr_dict[name].append(attr)

                elif attr.lower() == "data" and self.obj == "sourcefile":
                    # TODO: This is just a fix to keep FORD from crashing on
                    # encountering a block data structure. At some point I
                    # should actually implement support for them.
                    continue
                else:
                    self.print_error(line, f"Unexpected {attr.upper()} statement")

            elif match := self.END_RE.match(line):
                if isinstance(self, FortranSourceFile):
                    self.print_error(
                        line,
                        "END statement outside of any nesting",
                        describe_object=False,
                    )
                endtype = match.group(1)
                if endtype and endtype.lower() == "block":
                    blocklevel -= 1
                elif endtype and endtype.lower() == "associate":
                    associations.remove_last_batch()
                elif blocklevel == 0:
                    self._cleanup()
                    return

            elif (match := self.MODPROC_RE.match(line)) and (
                match["module"] or isinstance(self, FortranInterface)
            ):
                if isinstance(self, FortranInterface):
                    # Module procedure in an INTERFACE
                    self.modprocs.extend(get_mod_procs(source, match["names"], self))
                elif isinstance(self, FortranModule):
                    # Module procedure implementing an interface in a SUBMODULE
                    self.modprocedures.append(
                        FortranModuleProcedureImplementation(
                            source, match, self, self.permission
                        )
                    )
                    self.num_lines += self.modprocedures[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected MODULE PROCEDURE")

            elif match := self.BLOCK_DATA_RE.match(line):
                if hasattr(self, "blockdata"):
                    self.blockdata.append(FortranBlockData(source, match, self))
                    self.num_lines += self.blockdata[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected BLOCK DATA")
            elif self.BLOCK_RE.match(line):
                blocklevel += 1
            elif match := self.ASSOCIATE_RE.match(line):
                # Associations 'call' the rhs of the => operator
                self._add_procedure_calls(line, associations, line_no=lineno)

                # Register the associations
                assoc_batch = paren_split(",", strip_paren(match["associations"])[0])
                associations.add_batch(assoc_batch)

            elif match := self.MODULE_RE.match(line):
                if hasattr(self, "modules"):
                    self.modules.append(FortranModule(source, match, self))
                    self.num_lines += self.modules[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected MODULE")

            elif match := self.SUBMODULE_RE.match(line):
                if hasattr(self, "submodules"):
                    self.submodules.append(FortranSubmodule(source, match, self))
                    self.num_lines += self.submodules[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected SUBMODULE")

            elif match := self.PROGRAM_RE.match(line):
                if hasattr(self, "programs"):
                    self.programs.append(FortranProgram(source, match, self))
                    self.num_lines += self.programs[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected PROGRAM")
                if len(self.programs) > 1:
                    self.print_error(
                        line,
                        "Multiple PROGRAM units in same source file",
                        describe_object=False,
                    )

            elif match := self.SUBROUTINE_RE.match(line):
                if isinstance(self, FortranCodeUnit) and not incontains:
                    self.print_error(line, "Unexpected SUBROUTINE")
                elif hasattr(self, "subroutines"):
                    self.subroutines.append(
                        FortranSubroutine(source, match, self, self.permission)
                    )
                    self.num_lines += self.subroutines[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected SUBROUTINE")

            elif match := self.NAMELIST_RE.match(line):
                if hasattr(self, "namelists"):
                    self.namelists.append(
                        FortranNamelist(source, match, self, self.permission)
                    )
                else:
                    self.print_error(line, "Unexpected NAMELIST")

            elif match := self.FUNCTION_RE.match(line):
                if isinstance(self, FortranCodeUnit) and not incontains:
                    self.print_error(line, "Unexpected FUNCTION")
                elif hasattr(self, "functions"):
                    self.functions.append(
                        FortranFunction(source, match, self, self.permission)
                    )
                    self.num_lines += self.functions[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected FUNCTION")

            elif (match := self.TYPE_RE.match(line)) and blocklevel == 0:
                if hasattr(self, "types"):
                    self.types.append(FortranType(source, match, self, self.permission))
                    self.num_lines += self.types[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected derived TYPE")

            elif (match := self.INTERFACE_RE.match(line)) and blocklevel == 0:
                if hasattr(self, "interfaces"):
                    intr = FortranInterface(source, match, self, self.permission)
                    self.num_lines += intr.num_lines - 1
                    if intr.abstract:
                        self.absinterfaces.extend(intr.contents)
                    elif intr.generic:
                        self.interfaces.append(intr)
                    else:
                        self.interfaces.extend(intr.contents)
                else:
                    self.print_error(line, "Unexpected INTERFACE")

            elif (match := self.ENUM_RE.match(line)) and blocklevel == 0:
                if hasattr(self, "enums"):
                    self.enums.append(FortranEnum(source, match, self, self.permission))
                    self.num_lines += self.enums[-1].num_lines - 1
                else:
                    self.print_error(line, "Unexpected ENUM")

            elif (match := self.BOUNDPROC_RE.match(line)) and incontains:
                if not hasattr(self, "boundprocs"):
                    self.print_error(line, "Unexpected type-bound procedure")
                    continue

                names = match["names"].split(",")
                # Generic procedures or single name
                if match["generic"].lower() == "generic" or len(names) == 1:
                    self.boundprocs.append(
                        FortranBoundProcedure(source, match, self, child_permission)
                    )
                    continue

                # For multiple procedures, parse each one as if it
                # were on a line by itself
                for bind in reversed(names):
                    pseudo_line = self.BOUNDPROC_RE.match(
                        line[: match.start("names")] + bind
                    )
                    self.boundprocs.append(
                        FortranBoundProcedure(
                            source, pseudo_line, self, child_permission
                        )
                    )

            elif match := self.COMMON_RE.match(line):
                if hasattr(self, "common"):
                    split = self.COMMON_SPLIT_RE.split(line)
                    if len(split) > 1:
                        for i in range(len(split) // 2):
                            pseudo_line = (
                                split[0]
                                + " "
                                + split[2 * i + 1]
                                + " "
                                + split[2 * i + 2].strip()
                            )
                            if pseudo_line[-1] == ",":
                                pseudo_line = pseudo_line[:-1]
                            self.common.append(
                                FortranCommon(
                                    source,
                                    self.COMMON_RE.match(pseudo_line),
                                    self,
                                    "public",
                                )
                            )
                        for i in range(len(split) // 2):
                            self.common[-i - 1].doc_list = self.common[
                                -len(split) // 2 + 1
                            ].doc_list
                    else:
                        self.common.append(FortranCommon(source, match, self, "public"))
                else:
                    self.print_error(line, "Unexpected COMMON statement")

            elif (match := self.FINAL_RE.match(line)) and incontains:
                if hasattr(self, "finalprocs"):
                    procedures = self.SPLIT_RE.split(match.group(1).strip())
                    finprocs = [
                        FortranFinalProc(proc, self) for proc in procedures[:-1]
                    ]
                    finprocs.append(FortranFinalProc(procedures[-1], self, source))
                    self.finalprocs.extend(finprocs)
                else:
                    self.print_error(line, "Unexpected finalization procedure")

            elif self.VARIABLE_RE.match(line) and blocklevel == 0:
                if hasattr(self, "variables"):
                    self.variables.extend(
                        line_to_variables(source, line, child_permission, self)
                    )
                else:
                    self.print_error(line, "Unexpected variable")

            elif match := self.USE_RE.match(line):
                if hasattr(self, "uses"):
                    self.uses.append(list(match.groups()))
                else:
                    self.print_error(line, "Unexpected USE statement")

            elif self.ARITH_GOTO_RE.search(line):
                # Arithmetic GOTOs look a little like function references: "goto
                # (1, 2, 3) i". We don't do anything with these, but we do need
                # to disambiguate them from function calls
                continue

            elif (call_match := self.CALL_RE.search(line)) or (
                subcall_match := self.SUBCALL_RE.search(line)
            ):
                if not hasattr(self, "calls") and call_match:
                    # Not raising an error here as too much possibility that something
                    # has been misidentified as a function call
                    continue
                if not hasattr(self, "calls") and subcall_match:
                    self.print_error(line, "Unexpected procedure call")
                    continue

                self._add_procedure_calls(line, associations, line_no=lineno)

            else :
                self._member_access(line)



        if not isinstance(self, FortranSourceFile):
            raise Exception("File ended while still nested.")

    def restore_strings(self, line: str, strings: list) -> str:
        """
            Restores original string literals in a line by replacing tokens of the form "number"
            with their corresponding entries from the provided strings list.

            Args:
                line (str): The line containing tokenized string literals.
                strings (list): A list of original string literals saved prior to substitution.

            Returns:
                str: The line with the original string literals restored.
            """
        token_pattern = re.compile(r'"(\d+)"')
        # Use a lambda for inline replacement without defining an explicit 'repl' function.
        return token_pattern.sub(lambda match: strings[int(match.group(1))], line)
    
    def extract_filename_expr(self, raw_line: str) -> str:
        """
        Given a line like "open (108,file = hmd(i)%filename)",
        returns "hmd(i)%filename" (including any nested parentheses or // operations).
        """
        # find the file= token
        m = re.search(r'file\s*=', raw_line, re.IGNORECASE)
        if not m:
            return None

        # start just after the '='
        idx = m.end()
        # skip whitespace
        while idx < len(raw_line) and raw_line[idx].isspace():
            idx += 1

        # collect chars until we hit the closing ')' of the OPEN(...)
        depth = 0
        chars = []
        while idx < len(raw_line):
            ch = raw_line[idx]
            if ch == '(':
                depth += 1
                chars.append(ch)
            elif ch == ')':
                if depth == 0:
                    break   # this is the closing paren of open(...)
                depth -= 1
                chars.append(ch)
            else:
                chars.append(ch)
            idx += 1

        return ''.join(chars).strip()

    def _parse_io_open(self, line: str, line_no: int = None) -> None:
        raw = self.restore_strings(line, self.strings)
        low = raw.strip().lower()

        if low.startswith('open'):
            # Extract record length if present
            recl = None
            if m := self.RECL_RE.search(raw):
                recl = m.group(1)

            # Extract full filename expression
            fname = self.extract_filename_expr(raw)

            # Extract unit number
            unit_m = self.IO_UNIT_RE.search(raw)
            unit = unit_m.group('unit') if unit_m else None

            # Start a new session for this unit/file
            self.io_tracker.start(unit, fname,     line_no=line_no)

            # Record record-length metadata if found
            if recl is not None:
                self.io_tracker.record(unit, "meta", f"Record length: {recl}",     line_no=line_no)

            # Record the open itself
            self.io_tracker.record(unit, "open", raw,     line_no=line_no)
            return

        if low.startswith('read'):
            m = self.IO_UNIT_RE.search(raw)
            unit = m.group('unit') if m else None

            # Try to extract format information
            fmt = re.search(r'fmt\s*=\s*([^,)]+)', raw, re.IGNORECASE)
            if fmt:
                self.io_tracker.record(unit, "meta", f"Format: {fmt.group(1).strip()}",     line_no=line_no)

            self.io_tracker.record(unit, "read", raw,     line_no=line_no)
            return

        if low.startswith('write'):
            m = self.IO_UNIT_RE.search(raw)
            unit = m.group('unit') if m else None

            fmt = re.search(r'fmt\s*=\s*([^,)]+)', raw, re.IGNORECASE)
            if fmt:
                self.io_tracker.record_or_create(unit, "meta", f"Format: {fmt.group(1).strip()}",     line_no=line_no)

            self.io_tracker.record_or_create(unit, "write", raw,     line_no=line_no)
            return
        
        # record explicit file rewinds
        if low.startswith('rewind'):
            m = self.IO_UNIT_RE.search(raw)
            unit = m.group('unit') if m else None
            self.io_tracker.record(unit, "rewind", raw,     line_no=line_no)
            return    
        
        if low.startswith('backspace'):
            m = self.IO_UNIT_RE.search(raw)
            unit = m.group('unit') if m else None
            self.io_tracker.record(unit, "backspace", raw,     line_no=line_no)
            return

        if low.startswith('close'):
            m = self.IO_UNIT_RE.search(raw)
            unit = m.group('unit') if m else None
            self.io_tracker.record(unit, "close", raw,     line_no=line_no)
            self.io_tracker.close(unit)
            return

    def _parse_control_flow(self, line: str, line_no: int = None) -> None:
        """Parse control flow statements and update condition context."""
        if not hasattr(self, 'io_tracker'):
            return
            
        raw = self.restore_strings(line, self.strings)
        stripped = raw.strip().lower()
        
        # Handle if statements
        if stripped.startswith('if') and ('then' in stripped or '=' in stripped):
            # Extract the condition part
            if 'then' in stripped:
                condition_match = re.match(r'if\s*\((.+?)\)\s*then', stripped, re.IGNORECASE)
                if condition_match:
                    condition = f"if ({condition_match.group(1)})"
                    self.io_tracker.push_condition(condition, line_no)
            
        # Handle select case statements  
        elif stripped.startswith('select case'):
            case_match = re.match(r'select\s+case\s*\((.+?)\)', stripped, re.IGNORECASE)
            if case_match:
                condition = f"select case ({case_match.group(1)})"
                self.io_tracker.push_condition(condition, line_no)
        
        # Handle case statements
        elif stripped.startswith('case'):
            case_match = re.match(r'case\s*\((.+?)\)', stripped, re.IGNORECASE)
            if case_match:
                condition = f"case ({case_match.group(1)})"
                # Pop previous case and push new one
                if self.io_tracker.condition_stack and self.io_tracker.condition_stack[-1]['type'] == 'case':
                    self.io_tracker.pop_condition()
                self.io_tracker.push_condition(condition, line_no)
            elif 'default' in stripped:
                condition = "case default"
                if self.io_tracker.condition_stack and self.io_tracker.condition_stack[-1]['type'] == 'case':
                    self.io_tracker.pop_condition()
                self.io_tracker.push_condition(condition, line_no)
        
        # Handle else statements
        elif stripped.startswith('else') and not stripped.startswith('elseif'):
            condition = "else"
            self.io_tracker.push_condition(condition, line_no)
            
        # Handle elseif statements  
        elif stripped.startswith('elseif'):
            elseif_match = re.match(r'elseif\s*\((.+?)\)\s*then', stripped, re.IGNORECASE)
            if elseif_match:
                condition = f"elseif ({elseif_match.group(1)})"
                # Pop previous condition and push new one
                if self.io_tracker.condition_stack:
                    self.io_tracker.pop_condition()
                self.io_tracker.push_condition(condition, line_no)
        
        # Handle end statements
        elif stripped.startswith('end'):
            if any(end_kw in stripped for end_kw in ['endif', 'end if', 'endselect', 'end select']):
                if self.io_tracker.condition_stack:
                    self.io_tracker.pop_condition()

    def _add_procedure_calls(self,
                        line: str,
                        associations: Associations = Associations(),
                        line_no: int = None
                       ) -> None:
        """Helper to register procedure calls. For FortranProgram,
        FortranProcedure, and FortranModuleProcedureImplementation
        """

        # ==== Parse control flow statements ====
        self._parse_control_flow(line, line_no)
        
        # ==== call the new I/O parser ====
        self._parse_io_open(line, line_no)

        if not hasattr(self, "call_records"):
            self.call_records = []      # will be list of (chain, line_no)


        call_chains = []

        parendepth = 0
        _lines = ford.utils.strip_paren(line)

        # Match subcall, if present
        if match := self.SUBCALL_RE.search(_lines[0]):
            call_chains.append(match["call_chain"])
            # No function calls on this parendepth (because there's a subcall)
            parendepth += 1
            _lines = ford.utils.strip_paren(line, parendepth)

        # Match calls, and nested calls
        while len(_lines) > 0:
            for subline in _lines:
                # Process member access in the current subline
                self._member_access(subline)
                for match in self.CALL_RE.finditer(subline):
                    call_chains.append(match["call_chain"])
            parendepth += 1
            _lines = ford.utils.strip_paren(line, parendepth)

        # Add call chains to self.calls
        for chain_str in call_chains:
            call_chain = CALL_AND_WHITESPACE_RE.sub("", chain_str).lower().split("%")
            if call_chain[0] in associations:
                call_chain[0:1] = associations[call_chain[0]]
            if call_chain[-1] in INTRINSICS or call_chain[-1] in (
                call[-1] for call in self.calls
            ):
                continue
            self.calls.append(call_chain)

            # (2) record it alongside its source‐line for JSON later:
            self.call_records.append((call_chain, line_no))
            
    def _member_access(self, line: str) -> None:
        """
            Processes a single line of code to extract member access patterns
            and other unique items while avoiding duplicates.

            Parameters
            ----------
            line : str
                A line of code to process.
            """
        # Step 1: Format and clean the input line
        # Strip whitespace and split the line into components
        cleaned_line = line.strip()
        all_items = re.split(r"[,\s]+", cleaned_line)

        # Step 2: Remove all occurrences of `()`
        cleaned_items = [re.sub(r"\(\)", "", item).strip() for item in all_items if item.strip()]

        # Step 3: Further split items by '=' into key-value pairs
        split_items = []
        for item in cleaned_items:
            if "=" in item:
                split_items.extend(item.split("="))  # Split by '=' and keep both parts
            else:
                split_items.append(item)

        # Step 4: Initialize sets for deduplication
        existing_member_access = set(self.member_access_results)
        existing_other_results = set(self.other_results)

        # Step 5: Process cleaned and split items
        for item in split_items:
            # Remove standalone or leftover parentheses from items
            fully_cleaned_item = re.sub(r"[()]", "", item)

            # Check for `%`-based member access patterns using regex
            if self.MEMBER_ACCESS_RE.match(fully_cleaned_item):
                if fully_cleaned_item not in existing_member_access:
                    self.member_access_results.append(fully_cleaned_item)
                    existing_member_access.add(fully_cleaned_item)
            else:
                # Add non-member access items to other_results
                if fully_cleaned_item not in existing_other_results:
                    self.other_results.append(fully_cleaned_item)
                    existing_other_results.add(fully_cleaned_item)



    def _cleanup(self):
        raise NotImplementedError()

    def print_error(self, line, error, describe_object=True) -> None:
        description = f" in {self.obj} '{self.name}'" if describe_object else ""
        message = f"ERROR in file '{self.filename}': {error}{description}:\n\t{line}"
        if self.settings.dbg:
            return print(message)

        if self.settings.force:
            return
        raise ValueError(message)


class FortranCodeUnit(FortranContainer):
    """
    A class on which programs, modules, functions, and subroutines are based.
    """

    def _common_initialize(self) -> None:
        self.absinterfaces: List[FortranInterface] = []
        self.attr_dict: Dict[str, List[str]] = defaultdict(list)
        self.calls: List[Union[List[str], FortranProcedure]] = []
        self.common: List[FortranCommon] = []
        self.enums: List[FortranEnum] = []
        self.functions: List[FortranFunction] = []
        self.interfaces: List[FortranInterface] = []
        self.param_dict: Dict[str, str] = {}
        self.subroutines: List[FortranSubroutine] = []
        self.types: List[FortranType] = []
        self.uses: List[List[Union[str, FortranModule]]] = []
        self.variables: List[FortranVariable] = []
        self.all_procs: Dict[str, Union[FortranProcedure, FortranInterface]] = {}
        self.public_list: List[str] = []
        self.namelists: List[FortranNamelist] = []

  
    def _cleanup(self) -> None:        
        # finalize & print all I/O for this code‐unit
        self.io_tracker.finalize()
        self.io_tracker.report()

        # existing cleanup logic
        self.process_attribs()
        self.all_procs = {p.name.lower(): p for p in self.routines}
        for interface in self.interfaces:
            if not interface.abstract:
                self.all_procs[interface.name.lower()] = interface
            if interface.generic:
                for proc in interface.routines:
                    self.all_procs[proc.name.lower()] = proc
        self.variables = [v for v in self.variables if "external" not in v.attribs]

    def correlate(self, project: Project) -> None:
        # Add procedures, interfaces and types from parent to our lists
        self.all_procs.update(getattr(self.parent, "all_procs", {}))
        self.all_absinterfaces = getattr(self.parent, "all_absinterfaces", {})
        for ai in self.absinterfaces:
            self.all_absinterfaces[ai.name.lower()] = ai
        self.all_types = getattr(self.parent, "all_types", {})
        for dt in self.types:
            self.all_types[dt.name.lower()] = dt
        self.all_vars = getattr(self.parent, "all_vars", {})
        for var in self.variables:
            self.all_vars[var.name.lower()] = var
        # Add parent args/retval to all_vars if present
        for var in getattr(self.parent, "args", []):
            self.all_vars[var.name.lower()] = var
        if retvar := getattr(self.parent, "retvar", None):
            self.all_vars[retvar.name.lower()] = retvar

        if isinstance(self, FortranSubmodule):
            if isinstance(self.parent_submodule, FortranSubmodule):
                self.parent_submodule.descendants.append(self)
                self.all_procs.update(self.parent_submodule.all_procs)
                self.all_absinterfaces.update(self.parent_submodule.all_absinterfaces)
                self.all_types.update(self.parent_submodule.all_types)
            elif isinstance(self.ancestor_module, FortranModule):
                self.ancestor_module.descendants.append(self)
                self.all_procs.update(self.ancestor_module.all_procs)
                self.all_absinterfaces.update(self.ancestor_module.all_absinterfaces)
                self.all_types.update(self.ancestor_module.all_types)
                self.all_vars.update(self.ancestor_module.all_vars)

        # Module procedures will be missing (some/all?) metadata, so
        # now we copy it from the interface
        if isinstance(self, FortranModule):

            def assign_implementation_attributes(proc, base):
                if isinstance(proc, FortranModuleProcedureImplementation):
                    proc.attribs = base.attribs
                    proc.args = base.args
                    if hasattr(base, "retvar"):
                        proc.retvar = base.retvar
                    proc.proctype = base.proctype

            for proc in filter(lambda p: p.module, self.routines):
                intr = self.all_procs.get(proc.name.lower(), None)
                if isinstance(intr, FortranModuleProcedureInterface):
                    proc.module = intr
                    intr.procedure.module = proc
                    assign_implementation_attributes(proc, intr.procedure)
                # Some module procs are from procedures implemented withen a generic interface
                elif getattr(getattr(intr, "parent", None), "generic", False):
                    proc.module = intr
                    intr.module = proc
                    assign_implementation_attributes(proc, intr)

        def should_be_public(name: str) -> bool:
            """Is name public?"""
            return self.permission == "public" or name in self.public_list

# Function to print out all_vars
        #def print_all_vars(self):


        def filter_public(collection: dict) -> dict:
            """Return a new dict of only the public objects from collection"""
            return {
                name: obj for name, obj in collection.items() if should_be_public(name)
            }

        # Add procedures and types from USED modules to our lists
        for mod, extra in self.uses:
            if isinstance(mod, str):
                continue
            procs, absints, types, variables = mod.get_used_entities(extra)
            if isinstance(self, FortranModule):
                self.pub_procs.update(filter_public(procs))
                self.pub_absints.update(filter_public(absints))
                self.pub_types.update(filter_public(types))
                self.pub_vars.update(filter_public(variables))
            self.all_procs.update(procs)
            self.all_absinterfaces.update(absints)
            self.all_types.update(types)
            self.all_vars.update(variables)
        self.uses = set([m[0] for m in self.uses])

        typelist = {}
        for dtype in self.types:
            if dtype.extends and dtype.extends.lower() in self.all_types:
                dtype.extends = self.all_types[dtype.extends.lower()]
                typelist[dtype] = set([dtype.extends])
            else:
                typelist[dtype] = set([])
        typeorder = toposort.toposort_flatten(typelist)

        # Correlate types
        for dtype in typeorder:
            if dtype in self.types:
                dtype.correlate(project)

        # Match up called procedures
        if hasattr(self, "calls"):
            tmplst = []
            for call in self.calls:
                # get the item of the call
                item = self._find_chain_item(call)

                # failed to find item, give up and add call's string name to the list
                if item is None:
                    tmplst.append(call[-1])
                    continue

                # Don't register variables or type contructors, which sometimes get picked up as calls
                if not isinstance(item, (FortranVariable, FortranType)):
                    tmplst.append(item)
            self.calls = tmplst

        if isinstance(self, FortranSubmodule):
            self.ancestry: List[Union[str, FortranModule, FortranSubmodule]] = []
            item = self
            while item.parent_submodule:
                if isinstance(item.parent_submodule, str):
                    raise ValueError(
                        f"Unknown parent submodule '{item.parent_submodule}' of submodule '{item}'"
                    )
                item = item.parent_submodule
                self.ancestry.insert(0, item)
            self.ancestry.insert(0, item.ancestor_module)

        # Recurse
        for entity in self.iterator(
            "functions",
            "subroutines",
            "interfaces",
            "absinterfaces",
            "variables",
            "common",
            "modprocedures",
            "namelists",
        ):
            entity.correlate(project)
        if hasattr(self, "args") and not getattr(self, "mp", False):
            for arg in self.args:
                arg.correlate(project)
        if hasattr(self, "retvar") and not getattr(self, "mp", False):
            self.retvar.correlate(project)

        self.sort_components()

        # Separate module subroutines/functions from normal ones
        if self.obj == "submodule":
            self.modfunctions = [func for func in self.functions if func.module]
            self.functions = [func for func in self.functions if not func.module]
            self.modsubroutines = [sub for sub in self.subroutines if sub.module]
            self.subroutines = [sub for sub in self.subroutines if not sub.module]

    def process_attribs(self) -> None:
        """Attach standalone attributes to the correct object, and compute the
        list of public objects
        """

        # IMPORTANT: Make sure types processed before interfaces--import when
        # determining permissions of derived types and overridden constructors
        for item in self.iterator(
            "functions", "subroutines", "types", "interfaces", "absinterfaces"
        ):
            for attr in self.attr_dict[item.name.lower()]:
                if attr in ["public", "private", "protected"]:
                    item.permission = attr
                elif attr[0:4] == "bind":
                    if hasattr(item, "bindC"):
                        item.bindC = attr[5:-1]
                    elif getattr(item, "procedure", None):
                        item.procedure.bindC = attr[5:-1]
                    else:
                        item.attribs.append(attr)
                else:
                    item.attribs.append(attr)
            with suppress(KeyError):
                del self.attr_dict[item.name.lower()]

        for var in self.variables:
            for attr in self.attr_dict[var.name.lower()]:
                if attr in ["public", "private", "protected"]:
                    var.permission = attr
                elif attr[0:6] == "intent":
                    var.intent = attr[7:-1]
                elif DIM_RE.match(attr) and (
                    "pointer" in attr or "allocatable" in attr
                ):
                    i = attr.index("(")
                    var.attribs.append(attr[0:i])
                    var.dimension = attr[i:]
                elif attr == "parameter":
                    var.attribs.append(attr)
                    var.initial = self.param_dict[var.name.lower()]
                else:
                    var.attribs.append(attr)
            with suppress(KeyError):
                del self.attr_dict[var.name.lower()]

        # Now we want a list of all the objects we've declared, plus
        # any we've imported that have a "public" attribute
        self.public_list = [
            item.name.lower()
            for item in self.iterator(
                "functions",
                "subroutines",
                "types",
                "interfaces",
                "absinterfaces",
                "variables",
            )
            if item.permission == "public"
        ] + [item for item, attr in self.attr_dict.items() if "public" in attr]

        if self.settings.warn:
            for item, values in self.attr_dict.items():
                for value in values:
                    warn(
                        f"Unknown entity '{item}' with attribute '{value}' in {self.obj} "
                        f"'{self.name}' ('{self.filename}')"
                    )

        del self.attr_dict

    def prune(self):
        """
        Remove anything which shouldn't be displayed.
        """

        if self.obj == "proc" and not self.meta.proc_internals:
            self.functions = []
            self.subroutines = []
            self.types = []
            self.interfaces = []
            self.absinterfaces = []
            self.variables = []
            return

        self.functions = self.filter_display(self.functions)
        self.subroutines = self.filter_display(self.subroutines)
        self.types = self.filter_display(self.types)
        self.interfaces = self.filter_display(self.interfaces)
        self.absinterfaces = self.filter_display(self.absinterfaces)
        self.variables = self.filter_display(self.variables)
        if isinstance(self, FortranSubmodule):
            self.modprocedures = self.filter_display(self.modprocedures)
            self.modsubroutines = self.filter_display(self.modsubroutines)
            self.modfunctions = self.filter_display(self.modfunctions)

        # Recurse
        for obj in self.iterator(
            "absinterfaces",
            "interfaces",
        ):
            obj.visible = True

        for obj in self.iterator(
            "functions",
            "subroutines",
            "types",
            "modprocedures",
            "modfunctions",
            "modsubroutines",
        ):
            obj.visible = True
            obj.prune()

    def _find_chain_item(self, call_chain: List[str]) -> Optional[FortranBase]:
        """
        Traverse the call_chain to discover the item at the end of the chain.
        This is done by looking at the first label in the call chain and matching it to
        an arg, variable, function, or type in the current scope. Then, switch to the context of
        said item return and repeat until the call chain is exhausted.

        If the traversal fails to find a label in a context,
        the function gives up and returns None
        """

        def strip_type(s):
            """
            strip the encasing 'type()' or 'class()' from a string if it exists,
            and return the inner string (lowercased)
            """
            r = re.match(r"^(type|class)\((.*?)(?:\(.*\))?\)$", s, re.IGNORECASE)
            return r.group(2).lower() if r else s.lower()

        def get_label_item(context, label):
            """
            Return the item at label in the context, or None if it doesn't exist
            """
            # collect all labels that could potentially be in a call_chain
            labels = {}
            # procs
            labels.update(getattr(context, "all_procs", {}))
            # boundprocs
            labels.update(
                {bp.name.lower(): bp for bp in getattr(context, "boundprocs", [])}
            )
            # types
            labels.update(getattr(context, "all_types", {}))
            # extended type
            extend_type = context
            while extend_type := getattr(extend_type, "extends", None):
                if isinstance(extend_type, str):
                    break
                labels[extend_type.name.lower()] = extend_type
            # vars
            labels.update(getattr(context, "all_vars", {}))
            # local vars
            labels.update({a.name.lower(): a for a in getattr(context, "args", [])})
            if retvar := getattr(context, "retvar", None):
                labels[retvar.name.lower()] = retvar
            labels.update(
                {v.name.lower(): v for v in getattr(context, "variables", [])}
            )

            return labels.get(label, None)

        context: Optional[FortranBase] = self
        for call in call_chain[:-1]:
            item = get_label_item(context, call)

            # Find the context returned by the item
            if item is None:
                context = None
            elif hasattr(item, "retvar"):
                type_str = strip_type(item.retvar.full_type)
                context = item.all_types.get(type_str, None)
            elif isinstance(item, FortranType):
                context = item
            elif isinstance(item, FortranVariable):
                type_str = strip_type(item.full_type)
                if not (parent_all_types := getattr(item.parent, "all_types", {})):
                    return None
                context = parent_all_types.get(type_str, None)
            else:
                context = None

            if context is None:
                # failed to find context
                return None

        # return the item for the last label in the chain
        return get_label_item(context, call_chain[-1])


class FortranSourceFile(FortranContainer):
    """
    An object representing individual files containing Fortran code. A project
    will consist of a list of these objects. In turn, SourceFile objects will
    contains lists of all of that file's contents
    """

    def __init__(
        self,
        filepath: str,
        settings: ProjectSettings,
        preprocessor=None,
        fixed: bool = False,
        **kwargs,
    ):
        # Hack to prevent FortranBase.__str__ to generate an anchor link to the source file in HTML output.
        self.visible = kwargs.get("incl_src", True)
        self.path = filepath.strip()
        self.name = os.path.basename(self.path)
        self.settings = settings
        self.base_url = pathlib.Path(self.settings.project_url)
        self.fixed = fixed
        self.parent: Optional[FortranContainer] = None
        self.modules: List[FortranModule] = []
        self.submodules: List[FortranSubmodule] = []
        self.functions: List[FortranFunction] = []
        self.subroutines: List[FortranSubroutine] = []
        self.programs: List[FortranProgram] = []
        self.blockdata: List[FortranBlockData] = []
        self.doc_list = []
        self.hierarchy = []
        self.obj = "sourcefile"
        self.display = settings.display
        self.encoding = kwargs.get("encoding", True)
        self.permission = "public"

        # List of entities that need to have their docstrings converted to markdown
        self._to_be_markdowned: List[FortranBase] = []

        source = FortranReader(
            self.path,
            settings.docmark,
            settings.predocmark,
            settings.docmark_alt,
            settings.predocmark_alt,
            fixed,
            settings.fixed_length_limit,
            preprocessor,
            settings.macro,
            settings.include,
            settings.encoding,
        )

        super().__init__(source, "")
        self.read_metadata()
        self.raw_src = pathlib.Path(self.path).read_text(encoding=settings.encoding)
        lexer = FortranFixedLexer() if self.fixed else FortranLexer()
        self.src = highlight(
            self.raw_src,
            lexer,
            HtmlFormatter(lineanchors="ln", cssclass="hl codehilite"),
        )

    @property
    def markdownable_items(self):
        items = [self]

        for item in self._to_be_markdowned:
            # TODO: skip anything that isn't going to be displayed?
            if isinstance(item, FortranBase) and not hasattr(item, "external_url"):
                items.append(item)

        return items


class FortranModule(FortranCodeUnit):
    """
    An object representing individual modules within your source code. These
    objects contains lists of all of the module's contents, as well as its
    dependencies.
    """

    ONLY_RE = re.compile(r"^\s*,\s*only\s*:\s*(?=[^,])", re.IGNORECASE)
    RENAME_RE = re.compile(r"(\w+)\s*=>\s*(\w+)", re.IGNORECASE)

    def _initialize(self, line: re.Match) -> None:
        self.name = line["name"]
        self._common_initialize()
        del self.calls
        self.descendants: List[FortranSubmodule] = []
        self.modprocedures: List[FortranModuleProcedureImplementation] = []
        self.visible = True
        self.deplist: List[FortranModule] = []

    def _cleanup(self):
        """Create list of all local procedures. Ones coming from other modules
        will be added later, during correlation."""
        super()._cleanup()

        for var in self.variables:
            # Count procedure pointers and dummy procedures
            if var.vartype == "procedure":
                self.all_procs[var.name.lower()] = var

        def should_be_public(item: FortranBase) -> bool:
            return item.permission in ["public", "protected"]

        def filter_public(collection: list) -> dict:
            return {
                obj.name.lower(): obj for obj in collection if should_be_public(obj)
            }

        self.pub_procs = filter_public(self.all_procs.values())
        self.pub_vars = filter_public(self.variables)
        self.pub_types = filter_public(self.types)
        self.pub_absints = filter_public(self.absinterfaces)

    def get_used_entities(self, use_specs):
        """
        Returns the entities which are imported by a use statement. These
        are contained in dicts.
        """
        if len(use_specs.strip()) == 0:
            return (self.pub_procs, self.pub_absints, self.pub_types, self.pub_vars)

        only = bool(self.ONLY_RE.match(use_specs))
        use_specs = self.ONLY_RE.sub("", use_specs)
        # The used names after possible renaming
        used_names = {}
        for item in map(str.strip, use_specs.split(",")):
            if match := self.RENAME_RE.search(item):
                used_names[match.group(2).lower()] = match.group(1).lower()
            else:
                used_names[item.lower()] = item.lower()

        def used_objects(object_type: str, only: bool) -> dict:
            """Get the objects that are actually used"""
            result = {}
            object_collection = getattr(self, object_type)
            for name, obj in object_collection.items():
                name = name.lower()
                if only:
                    if name in used_names:
                        result[used_names[name]] = obj
                else:
                    result[name] = obj
            return result

        ret_procs = used_objects("pub_procs", only)
        ret_absints = used_objects("pub_absints", only)
        ret_types = used_objects("pub_types", only)
        ret_vars = used_objects("pub_vars", only)
        return (ret_procs, ret_absints, ret_types, ret_vars)


class FortranSubmodule(FortranModule):
    def _initialize(self, line: re.Match) -> None:
        super()._initialize(line)
        self.parent_submodule: Union[str, None, FortranSubmodule] = line[
            "parent_submod"
        ]
        self.ancestor_module: Union[str, FortranModule] = line["ancestor_module"]
        del self.public_list

    def get_dir(self):
        return "module"


def _list_of_procedure_attributes(
    attribute_string: Optional[str],
) -> Tuple[List[str], str]:
    """Convert a string of attributes into a list of attributes"""
    if not attribute_string:
        return [], ""

    attribute_list = []
    attribute_string = attribute_string.lower()

    for attribute in [
        "impure",
        "pure",
        "elemental",
        "non_recursive",
        "recursive",
        "module",
    ]:
        if attribute in attribute_string:
            attribute_list.append(attribute)
            attribute_string = re.sub(
                attribute, "", attribute_string, flags=re.IGNORECASE
            )

    return attribute_list, attribute_string.replace(" ", "")


def implicit_type(name: str) -> str:
    """Map names to implicit types"""

    if name[0].lower() in "ijklmn":
        return "integer"
    return "real"


class FortranProcedure(FortranCodeUnit):
    """Base class for subroutines and functions for common functionality"""

    proctype = "Unknown"

    def _procedure_initialize(
        self,
        name: str,
        arguments: Optional[str],
        attributes: Optional[str],
        bindC: Optional[str],
        **kwargs,
    ) -> str:
        self.name = name
        self.attribs, attribstr = _list_of_procedure_attributes(attributes)
        self.mp = False
        self.module = "module" in self.attribs

        self.args = []
        if arguments:
            # Empty argument lists will contain the empty string, so we need to remove it
            self.args = [
                arg for arg in self.SPLIT_RE.split(arguments[1:-1].strip()) if arg
            ]

        self._parse_bind_C(bindC)
        self._common_initialize()

        return attribstr

    def _parse_bind_C(self, bind_C_text: Optional[str]):
        """Parses a `bind(...)` attribute"""

        if bind_C_text is None:
            self.bindC = None
            return

        # Shouldn't have parentheses in, but just to be safe, let's
        # remove any
        if "(" in bind_C_text or ")" in bind_C_text:
            bind_C_text = ford.utils.get_parens(bind_C_text, -1)

        self.bindC = bind_C_text

        if self.parent is None:
            return

        # Now we have to replace any quoted text that has previously
        # been removed
        search_from = 0
        while quote := QUOTES_RE.search(self.bindC[search_from:]):
            num = int(quote.group()[1:-1])
            self.bindC = self.bindC[0:search_from] + QUOTES_RE.sub(
                self.parent.strings[num], self.bindC[search_from:], count=1
            )
            if not (next_match := QUOTES_RE.search(self.bindC[search_from:])):
                raise ValueError(
                    f"Unexpected missing quotes in '{self.bindC[search_from:]}'"
                )
            search_from += next_match.end(0)

    @property
    def is_interface_procedure(self) -> bool:
        """Is this procedure just an interface?"""
        return isinstance(self.parent, FortranInterface) and not self.parent.generic

    @property
    def permission(self):
        """Permission (public/private) of this procedure"""
        if self.is_interface_procedure:
            return self.parent.permission

        return self._permission

    @permission.setter
    def permission(self, value):
        self._permission = value

    @property
    def ident(self) -> str:
        """Return a unique identifier for this object"""
        if self.is_interface_procedure:
            return namelist.get_name(self.parent)
        return super().ident

    def get_dir(self) -> Optional[str]:
        if self.is_interface_procedure:
            return "interface"

        return super().get_dir()

    def _cleanup(self):
        """Convert all child entities to object instances"""
        super()._cleanup()

        for i, arg in enumerate(self.args):
            # Is there a variable declaration for this argument?
            for var in self.variables:
                if arg.lower() == var.name.lower():
                    arg = var
                    self.variables.remove(var)
                    break

            # Otherwise, is it a procedure with an interface?
            if isinstance(arg, str):
                for intr in self.interfaces:
                    if intr.abstract or intr.generic:
                        continue
                    proc = intr.procedure
                    if proc.name.lower() == arg.lower():
                        arg = proc
                        arg.parent = self
                        self.interfaces.remove(intr)
                        break

            # If we've still not found it, it's an implicitly-type variable.
            # FIXME: we pay no attention to `implicit none` or other
            # `implicit` statements
            if isinstance(arg, str):
                arg = FortranVariable(arg, implicit_type(arg), self, doc="")

            self.args[i] = arg

    @property
    def local_variables(self):
        """Return variables that are declared locally within this procedure (excluding arguments)."""
        local_vars = []
        
        # Get variables that are declared in this procedure
        if hasattr(self, 'variables'):
            for var in self.variables:
                # Variable is local if its parent is this procedure or if parent is None (could be local)
                if getattr(var, 'parent', None) == self or getattr(var, 'parent', None) is None:
                    # Don't include arguments
                    if not hasattr(self, 'args') or var not in self.args:
                        local_vars.append(var)
        
        # Always try to extract from source as fallback or supplement
        try:
            source_vars = self._extract_local_variables_from_source()
            
            # Combine and deduplicate
            existing_names = set(getattr(var, 'name', str(var)) for var in local_vars)
            for var in source_vars:
                if var.name not in existing_names:
                    local_vars.append(var)
        except Exception as e:
            # In case of any error, just continue with what we have
            pass
        
        return local_vars
    
    def _extract_local_variables_from_source(self):
        """Extract local variable declarations from source code."""
        import re
        local_vars = []
        
        # Get the source code - try to read from source file
        source_text = None
        if hasattr(self, 'source_file') and self.source_file:
            try:
                # Read the source file directly
                with open(self.source_file.path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_source = f.read()
                
                # Extract just the procedure's source code
                # Find the procedure start and end
                proc_start_pattern = rf'^\s*{self.proctype.lower()}\s+{re.escape(self.name)}\b'
                proc_end_pattern = rf'^\s*end\s+{self.proctype.lower()}\b'
                
                source_lines = full_source.split('\n')
                in_procedure = False
                procedure_lines = []
                
                for line in source_lines:
                    if re.match(proc_start_pattern, line.strip(), re.IGNORECASE):
                        in_procedure = True
                        procedure_lines.append(line)
                    elif in_procedure:
                        procedure_lines.append(line)
                        if re.match(proc_end_pattern, line.strip(), re.IGNORECASE):
                            break
                
                if procedure_lines:
                    source_text = '\n'.join(procedure_lines)
                    
            except Exception as e:
                return local_vars
        else:
            # Fallback to other attributes
            if hasattr(self, 'src') and self.src:
                source_text = self.src
            elif hasattr(self, 'raw_src') and self.raw_src:
                source_text = self.raw_src
            elif hasattr(self, 'source') and self.source:
                source_text = self.source
            else:
                return local_vars
        
        if not source_text:
            return local_vars
        
        # Convert to string if it's not already
        if not isinstance(source_text, str):
            source_text = str(source_text)
            
        # Enhanced regex patterns to find variable declarations
        var_patterns = [
            # Character declarations with :: and specific length (with space)
            r'^\s*character\s+\(\s*len\s*=\s*\d+\s*\)\s*::\s*([^!]+)',
            # Character declarations without :: and specific length (with space)
            r'^\s*character\s+\(\s*len\s*=\s*\d+\s*\)\s+([^!=,\n]+)(?:\s*=.*)?(?:\s*!.*)?$',
            # Standard declaration with :: 
            r'^\s*(integer|real|logical|double\s+precision)(?:\s*\([^)]*\))?\s*::\s*([^!]+)',
            # Older Fortran style without :: (more common in the test files)
            r'^\s*(integer|real|logical|double\s+precision)(?:\s*\([^)]*\))?\s+([^!=,\n]+)(?:\s*=.*)?(?:\s*!.*)?$',
        ]
        
        source_lines = source_text.split('\n')
        
        for line in source_lines:
            line_stripped = line.strip()
            
            # Skip comment lines, empty lines, and continuation lines
            if not line_stripped or line_stripped.startswith('!'):
                continue
            # Only skip if it's actually a comment line (starts with 'c' or 'C' followed by space or not alphanumeric)
            if line_stripped.lower().startswith('c ') or (line_stripped.lower().startswith('c') and len(line_stripped) > 1 and not line_stripped[1].isalnum()):
                continue
            if line.startswith('     ') and len(line) > 5 and line[5] in ['&', '+', '*']:  # Fortran continuation
                continue
                
            for pattern in var_patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    if pattern.startswith(r'^\s*character'):
                        # Character variable
                        var_type = "character"
                        var_declarations = match.group(1).strip()
                    else:
                        # Other types
                        var_type = match.group(1)
                        var_declarations = match.group(2).strip()
                    
                    # Parse variable names (handle multiple variables on one line)
                    var_names = []
                    for name in var_declarations.split(','):
                        # Clean up variable name (remove initialization, dimensions, etc.)
                        clean_name = name.strip().split('=')[0].strip()
                        clean_name = re.sub(r'\([^)]*\)', '', clean_name).strip()  # Remove array dimensions
                        clean_name = re.sub(r'\s*!.*$', '', clean_name).strip()    # Remove comments
                        if clean_name and clean_name.replace('_', '').replace(' ', '').isalnum():
                            var_names.append(clean_name)
                    
                    for var_name in var_names:
                        # Skip if variable name is empty or is an argument
                        if not var_name:
                            continue
                        if hasattr(self, 'args') and any(arg.name == var_name if hasattr(arg, 'name') else str(arg) == var_name for arg in self.args):
                            continue
                            
                        # Create a mock variable object with the required interface
                        class MockVariable:
                            def __init__(self, name, var_type, parent):
                                self.obj = 'variable'
                                self.name = name
                                self.var_type = var_type
                                self.full_type = var_type
                                self.parent = parent
                                self.dimension = ""
                                self.anchor = f"var-{name.lower()}"
                                self.intent = None
                                self.optional = False
                                self.permission = "private"
                                self.parameter = False
                                self.attribs = []
                                self.initial = None
                                
                            def meta(self, key):
                                if key == 'summary':
                                    return f"Local variable of type {self.var_type}"
                                return ""
                        
                        mock_var = MockVariable(var_name, var_type, self)
                        local_vars.append(mock_var)
                    break  # Found a match, no need to try other patterns for this line
        
        return local_vars

    @property 
    def non_local_variables(self):
        """Return variables that are not declared locally (arguments, parameters, etc.)."""
        non_local_vars = []
        
        # Include arguments
        if hasattr(self, 'args'):
            non_local_vars.extend(self.args)
        
        # Include variables that are not local to this procedure
        if hasattr(self, 'variables'):
            for var in self.variables:
                if getattr(var, 'parent', None) != self:
                    non_local_vars.append(var)
        
        return non_local_vars

    @property
    def outside_variables_used(self):
        """Return variables and types from outside modules that are used in this procedure."""
        outside_vars = []
        
        # Get variables from uses
        if hasattr(self, 'uses'):
            for use in self.uses:
                # Handle different use statement formats
                if isinstance(use, (list, tuple)) and len(use) >= 1:
                    module = use[0]
                    if hasattr(module, 'variables'):
                        # If specific items are imported (like "use module, only: var1, var2")
                        if len(use) > 2 and use[1] == "only":
                            for item_name in use[2:]:
                                for var in module.variables:
                                    if var.name.lower() == item_name.lower():
                                        outside_vars.append(var)
                        else:
                            # If whole module is used (like "use module")
                            # Add first few variables as examples
                            outside_vars.extend(module.variables[:5])  # Limit to avoid too many
                elif hasattr(use, 'variables'):
                    # Direct module reference
                    outside_vars.extend(use.variables[:5])
        
        # If no variables found from uses, create mock entries for the modules used
        if not outside_vars and hasattr(self, 'uses'):
            for use in self.uses:
                module_name = None
                if isinstance(use, (list, tuple)) and len(use) >= 1:
                    module_name = getattr(use[0], 'name', str(use[0]))
                elif hasattr(use, 'name'):
                    module_name = use.name
                
                if module_name:
                    # Create a mock variable representing the module usage
                    mock_var = type('MockModuleUsage', (), {
                        'name': module_name.replace('_module', ''),
                        'full_type': f"from {module_name}",
                        'parent': type('MockModule', (), {'name': module_name})(),
                        'meta': lambda self, key: f"Variables and types from {module_name}"
                    })()
                    outside_vars.append(mock_var)
        
        # Remove duplicates by name
        seen_names = set()
        unique_vars = []
        for var in outside_vars:
            if hasattr(var, 'name') and var.name.lower() not in seen_names:
                seen_names.add(var.name.lower())
                unique_vars.append(var)
        
        return unique_vars

    @property
    def io_operations(self):
        """Return I/O operations from the io_tracker."""
        if hasattr(self, 'io_tracker'):
            self.io_tracker.finalize()
            return self.io_tracker.summarize_file_io()
        return {}


class FortranSubroutine(FortranProcedure):
    """
    An object representing a Fortran subroutine and holding all of said
    subroutine's contents.
    """

    proctype = "Subroutine"

    def _initialize(self, line: re.Match) -> None:
        self._procedure_initialize(**line.groupdict())


class FortranFunction(FortranProcedure):
    """
    An object representing a Fortran function and holding all of said function's
    contents.
    """

    proctype = "Function"

    def _initialize(self, line: re.Match) -> None:
        attribstr = self._procedure_initialize(**line.groupdict())
        self.retvar = line["result"] or self.name

        with suppress(ValueError):
            parsed_type = parse_type(
                attribstr, self.strings, self.settings.extra_vartypes
            )
            self.retvar = FortranVariable(
                name=self.retvar,
                vartype=parsed_type.vartype,
                parent=self,
                kind=parsed_type.kind,
                strlen=parsed_type.strlen,
                proto=parsed_type.proto,
            )

    def _cleanup(self):
        if not isinstance(self.retvar, FortranVariable):
            for var in self.variables:
                if var.name.lower() == self.retvar.lower():
                    self.retvar = var
                    self.variables.remove(var)
                    break
            else:
                self.retvar = FortranVariable(
                    self.retvar, implicit_type(self.retvar), self
                )

        super()._cleanup()


class FortranModuleProcedureImplementation(FortranCodeUnit):
    """An object representing a the implementation of a Module
    Function or Module Subroutine in a submodule. The interface is
    represented separately by a `FortranModuleProcedureInterface`

    """

    module = True
    proctype = "Module Procedure"

    def _initialize(self, line: re.Match) -> None:
        self.name = line["names"]

        self._common_initialize()
        self.mp = True
        self.attribs: List[str] = []
        self.args: List[str] = []
        self.retvar = None


class FortranProgram(FortranCodeUnit):
    """
    An object representing the main Fortran program.
    """

    def _initialize(self, line: re.Match) -> None:
        self.name = line.group(1)
        if self.name is None:
            self.name = ""
        self._common_initialize()


class FortranNamelist(FortranBase):
    """
    An object representing a Fortran namelist and holding all of said
    namelist's contents
    """

    def _initialize(self, line: re.Match) -> None:
        self.variables = [
            variable.strip().lower() for variable in line["vars"].split(",")
        ]
        self.name = line["name"]
        self.visible = True

    def correlate(self, project):
        all_vars: Dict[str, FortranVariable] = {}

        all_vars.update(self.parent.all_vars)
        if isinstance(self.parent, FortranProcedure):
            all_vars.update({arg.name: arg for arg in self.parent.args})

        self.variables = [
            all_vars.get(variable, variable) for variable in self.variables
        ]


class FortranType(FortranContainer):
    """
    An object representing a Fortran derived type and holding all of said type's
    components and type-bound procedures. It also contains information on the
    type's inheritance.
    """

    def _initialize(self, line: re.Match) -> None:
        self.name = line.group(2)
        self.extends = None
        self.attribs = []
        if line.group(1):
            attribstr = line.group(1)[1:].strip()
            attriblist = self.SPLIT_RE.split(attribstr.strip())
            for attrib in attriblist:
                attrib_lower = attrib.strip().lower()
                if extends := EXTENDS_RE.search(attrib):
                    self.extends = extends["base"]
                elif attrib_lower in ["public", "private"]:
                    self.permission = attrib_lower
                elif attrib_lower == "external":
                    self.attribs.append("external")
                else:
                    self.attribs.append(attrib.strip())
        if line.group(3):
            paramstr = line.group(3).strip()
            self.parameters = self.SPLIT_RE.split(paramstr)
        else:
            self.parameters = []
        self.sequence = False
        self.variables: List[FortranVariable] = []
        self.boundprocs: List[FortranBoundProcedure] = []
        self.finalprocs: List[FortranFinalProc] = []
        self.constructor: Optional[FortranSubroutine] = None

    def _cleanup(self):
        # finish any half‑open sessions and emit their reports
        self.io_tracker.finalize()
        self.io_tracker.report()

        # Match parameters with variables
        for i in range(len(self.parameters)):
            for var in self.variables:
                if self.parameters[i].lower() == var.name.lower():
                    self.parameters[i] = var
                    self.variables.remove(var)
                    break

    def correlate(self, project):
        self.all_absinterfaces = self.parent.all_absinterfaces
        self.all_types = self.parent.all_types
        self.all_procs = self.parent.all_procs
        self.num_lines_all = self.num_lines

        # Match variables as needed (recurse)
        for v in self.variables:
            v.correlate(project)

        if self.extends and isinstance(self.extends, str):
            warn(
                f"Could not find base type ('{self.extends}') of derived type '{self.name}' "
                f"(in '{self.filename}').\n"
                f"         If '{self.extends}' is defined in an external module, you may be "
                "able to tell Ford about its documentation\n"
                "         with the `extra_mods` setting"
            )

        # Get inherited public components
        inherited = [
            var
            for var in getattr(self.extends, "variables", [])
            if var.permission == "public"
        ]
        self.local_variables = self.variables
        for invar in inherited:
            if not hasattr(invar, "doc"):
                invar.doc = f"Inherited from [[{self.extends}]]"
                invar.meta = EntitySettings()
        self.variables = inherited + self.variables

        # Match boundprocs with procedures
        # FIXME: This is not at all modular because must process non-generic
        # bound procs first--could there be a better way to do it
        for proc in self.boundprocs:
            if not proc.generic:
                proc.correlate(project)
        # Identify inherited type-bound procedures which are not overridden
        inherited = []
        inherited_generic = []
        if self.extends and not isinstance(self.extends, str):
            for bp in self.extends.boundprocs:
                if bp.permission == "private":
                    continue
                if all([bp.name.lower() != b.name.lower() for b in self.boundprocs]):
                    if bp.generic:
                        gen = copy.copy(bp)
                        gen.parent = self
                        inherited.append(gen)
                    else:
                        inherited.append(bp)
                elif bp.generic:
                    gen = copy.copy(bp)
                    gen.parent = self
                    inherited_generic.append(gen)
        self.boundprocs = inherited + self.boundprocs
        # Match up generic type-bound procedures to their particular bindings
        for proc in self.boundprocs:
            if type(proc) is FortranBoundProcedure:
                for bp in inherited_generic:
                    if bp.name.lower() == proc.name.lower() and isinstance(
                        bp, FortranBoundProcedure
                    ):
                        proc.bindings = bp.bindings + proc.bindings
                        break
                if proc.generic:
                    proc.correlate(project)
        # Match finalprocs
        for fp in self.finalprocs:
            fp.correlate(project)
        # Find a constructor, if one exists
        if self.name.lower() in self.all_procs:
            self.constructor = self.all_procs[self.name.lower()]
            self.constructor.permission = self.permission
            self.num_lines += getattr(
                self.constructor, "num_lines_all", self.constructor.num_lines
            )

        self.sort_components()

        # Get total num_lines, including implementations
        for proc in self.finalprocs:
            self.num_lines_all += proc.procedure.num_lines

        for proc in self.boundprocs:
            self.num_lines_all += proc.num_lines

    def prune(self):
        """
        Remove anything which shouldn't be displayed.
        """
        self.boundprocs = self.filter_display(self.boundprocs)
        self.variables = self.filter_display(self.variables)
        for obj in self.boundprocs + self.variables:
            obj.visible = True

    def __repr__(self):
        return f"FortranType('{self.name}', variables={self.variables}, boundprocs={self.boundprocs})"


class FortranEnum(FortranContainer):
    """
    An object representing a Fortran enumeration. Contains the individual
    enumerators as variables.
    """

    def _initialize(self, line: re.Match) -> None:
        self.variables: List[FortranVariable] = []
        self.name = ""

    def _cleanup(self):
        # finish any half‑open sessions and emit their reports
        self.io_tracker.finalize()
        self.io_tracker.report()

        prev_val = -1
        for var in self.variables:
            if not var.initial:
                var.initial = prev_val + 1
            initial = (
                remove_kind_suffix(var.initial)
                if isinstance(var.initial, str)
                else var.initial
            )
            try:
                prev_val = int(initial)
            except ValueError:
                raise ValueError(
                    f"Non-integer ('{var.initial}') assigned to enumerator '{var.name}'."
                )


class FortranInterface(FortranContainer):
    """An ``interface`` block, including generic and abstract interfaces

    Attributes
    ----------
    subroutines: list
        External subroutines
    functions: list
        External functions
    modprocs: list
        Procedures defined in this scope
    variables: list
        Procedure pointers and dummy procedures
    generic: bool
        True if this is a generic interface
    abstract: bool
        True if this is an abstract interface
    """

    proctype = "Interface"

    def _initialize(self, line: re.Match) -> None:
        self.name = line.group(2)
        self.subroutines: List[FortranSubroutine] = []
        self.functions: List[FortranFunction] = []
        self.modprocs: List[FortranModuleProcedureReference] = []
        self.variables: List[FortranVariable] = []
        self.generic = bool(self.name)
        self.abstract = bool(line.group(1))
        if self.generic and self.abstract:
            raise Exception(f"Generic interface '{self.name}' can not be abstract")

        if self.abstract:
            self.source_file._to_be_markdowned.remove(self)

    def correlate(self, project):
        self.all_absinterfaces = self.parent.all_absinterfaces
        self.all_types = self.parent.all_types
        self.all_procs = self.parent.all_procs
        self.num_lines_all = self.num_lines
        if self.generic:
            # Some "modprocs" are actually procedure pointers or dummy
            # args, so we need to move them to a separate lsit
            modprocs_to_pop = []
            for modproc in self.modprocs:
                try:
                    procedure = self.all_procs[modproc.name.lower()]
                except KeyError:
                    raise RuntimeError(
                        f"Could not find interface procedure '{modproc.name}' in '{self.parent.name}'. "
                        f"Known procedures are: {list(self.all_procs.keys())}"
                    )

                if isinstance(procedure, FortranVariable):
                    self.variables.append(procedure)
                    modprocs_to_pop.append(modproc)
                    continue

                modproc.procedure = procedure
                self.num_lines_all += modproc.procedure.num_lines

            for proc in modprocs_to_pop:
                self.modprocs.remove(proc)

            for proc in self.routines:
                proc.correlate(project)
        else:
            self.procedure.correlate(project)

        self.sort_components()

    def _cleanup(self):
        # finish any half‑open sessions and emit their reports
        self.io_tracker.finalize()
        self.io_tracker.report()

        if not self.abstract and self.generic:
            return

        contents = []
        for proc in self.routines:
            proc.visible = False
            contents.append(FortranModuleProcedureInterface(proc, self, self.doc_list))
        self.contents = contents

    def get_dir(self) -> Optional[str]:
        # Unnamed interfaces don't have separate pages
        if self.name:
            return super().get_dir()
        return None


class FortranModuleProcedureInterface(FortranInterface):
    """The interface part of a `FortranModuleProcedureImplementation`

    This should be created directly by a `FortranInterface`

    Not to be confused with a `FortranModuleProcedureReference` which is merely
    a reference to a module procedure defined elsewhere, whereas a
    `FortranModuleProcedureInterface` is a complete interface to a
    module procedure

    """

    proctype = "Interface"
    abstract = False
    generic = False
    obj = "interface"

    def __init__(
        self, procedure: FortranProcedure, parent: FortranInterface, doc_list: List[str]
    ):
        self.parent = parent.parent
        self.parobj = self.parent.obj if self.parent else None
        self.settings = parent.settings
        self.base_url = pathlib.Path(self.settings.project_url)
        self.visible = parent.visible
        self.num_lines = parent.num_lines
        self.doc_list = doc_list
        self.variables = copy.copy(parent.variables)

        self.procedure = procedure
        self.name = procedure.name
        self.permission = procedure.permission
        self.procedure.parent = self

        self.hierarchy = self._make_hierarchy()
        self.read_metadata()
        self.source_file._to_be_markdowned.append(self)


class FortranFinalProc(FortranBase):
    """
    An object representing a finalization procedure for a derived type
    within Fortran.
    """

    def __init__(self, name, parent, source=None):
        self.name = name
        self.parent = parent
        self.procedure = None
        self.obj = "finalproc"
        self.parobj = self.parent.obj
        self.display = self.parent.display
        self.settings = self.parent.settings
        self.base_url = pathlib.Path(self.settings.project_url)
        self.doc_list = read_docstring(source, self.settings.docmark) if source else []
        self.hierarchy = self._make_hierarchy()
        self.read_metadata()
        self.source_file._to_be_markdowned.append(self)

    def correlate(self, project):
        self.all_procs = self.parent.all_procs
        if self.name.lower() in self.all_procs:
            self.procedure = self.all_procs[self.name.lower()]


class FortranVariable(FortranBase):
    """
    An object representing a variable within Fortran.
    """

    def __init__(
        self,
        name,
        vartype,
        parent,
        attribs=[],
        intent="",
        optional=False,
        permission="public",
        parameter=False,
        kind=None,
        strlen=None,
        proto=None,
        doc=None,
        points=False,
        initial=None,
        line_number=None,  # <-- NEW!
    ):
        # ---- Call base class init! ----
        super().__init__(
            source=parent.source_file if parent and hasattr(parent, "source_file") else None,
            first_line=None,
            parent=parent,
            inherited_permission=permission,
            strings=None,
            line_number=line_number,
        )
        # ---- End call to base ----

        self.name = name
        self.vartype = vartype.lower()
        self.parent = parent
        if self.parent:
            self.parobj = self.parent.obj
            self.settings = self.parent.settings
        else:
            self.parobj = None
            self.settings = None
        self.base_url = pathlib.Path(
            self.settings.project_url if self.settings else "."
        )
        self.obj = type(self).__name__[7:].lower()
        self.attribs = copy.copy(attribs)
        self.intent = intent
        self.optional = optional
        self.kind = kind
        self.strlen = strlen
        self.proto = copy.copy(proto)
        self.doc_list = copy.copy(doc) if doc is not None else []
        self.permission = permission
        self.points = points
        self.parameter = parameter
        self.initial = initial
        self.dimension = ""
        self.visible = False
        self.ug = False
        self.ug2 = False

        indexlist = []
        indexparen = self.name.find("(")
        if indexparen > 0:
            indexlist.append(indexparen)
        indexbrack = self.name.find("[")
        if indexbrack > 0:
            indexlist.append(indexbrack)
        indexstar = self.name.find("*")
        if indexstar > 0:
            indexlist.append(indexstar)

        if len(indexlist) > 0:
            self.dimension = self.name[min(indexlist) :]
            self.name = self.name[0 : min(indexlist)]

        self.hierarchy = self._make_hierarchy()
        self.read_metadata()
        self.source_file._to_be_markdowned.append(self)


    def correlate(self, project):
        if not self.proto:
            return

        proto_name = self.proto[0].lower()
        if proto_name == "*":
            return

        if self.vartype in ("type", "class"):
            self.proto[0] = self.parent.all_types.get(proto_name, self.proto[0])
        elif self.vartype == "procedure":
            abstract_prototype = self.parent.all_absinterfaces.get(
                proto_name, self.proto[0]
            )
            self.proto[0] = self.parent.all_procs.get(proto_name, abstract_prototype)

    @property
    def full_type(self):
        """Return the full type, including class, kind, len, and so on"""
        parameter_parts = []
        result = self.vartype

        # Wrap only kind, strlen, proto in brackets
        if self.kind:
            parameter_parts.append(f"kind={self.kind}")
        if self.strlen:
            parameter_parts.append(f"len={self.strlen}")

        # If we've got a "proto", then we probably don't have kind and strlen?
        if parameter_parts:
            result += f"({', '.join(parameter_parts)})"
        elif self.proto:
            proto = str(self.proto[0])
            if self.proto[1]:
                proto += f"({self.proto[1]})"
            result += f"({proto})"

        return result

    @property
    def full_declaration(self):
        """Return the full type declaration, including attributes, dimensions,
        kind, and so on"""

        # Add all the other attributes to a single list
        attribute_parts = copy.copy(self.attribs)
        if self.dimension:
            attribute_parts.append(self.dimension)
        if self.parameter:
            attribute_parts.append("parameter")

        # Note: not str.join because we want the leading comman too
        attributes = [f", {part}" for part in attribute_parts]
        return f"{self.full_type}{''.join(attributes)}"

    def __repr__(self):
        return f"FortranVariable('{self.name}', type='{self.full_type}', permission='{self.permission}')"


class FortranBoundProcedure(FortranBase):
    """
    An object representing a type-bound procedure, possibly overloaded.
    """

    def _initialize(self, line: re.Match) -> None:
        self.attribs: List[str] = []
        self.deferred = False
        """Is a deferred procedure"""
        self.protomatch = False
        """Prototype has been matched to procedure"""

        for attribute in ford.utils.paren_split(",", line["attributes"] or ""):
            attribute = attribute.strip().lower()
            if not attribute:
                continue

            if attribute in ["public", "private"]:
                self.permission = attribute
            elif attribute == "deferred":
                self.deferred = True
            else:
                self.attribs.append(attribute)

        split = self.POINTS_TO_RE.split(line["names"])
        self.name = split[0].strip()
        self.generic = line["generic"].lower() == "generic"
        self.proto = line["prototype"]
        if self.proto:
            self.proto = self.proto[1:-1].strip()

        binds = self.SPLIT_RE.split(split[1]) if len(split) > 1 else (self.name,)
        self.bindings: List[Union[str, FortranProcedure, FortranBoundProcedure]] = [
            bind.strip() for bind in binds
        ]

    @property
    def binding_type(self) -> str:
        """String representation of binding type"""
        if self.generic:
            return "generic"

        if not self.proto:
            return "procedure"

        if self.protomatch and not self.proto.visible:
            return f"procedure({self.proto.name})"

        return f"procedure({self.proto})"

    @property
    def full_declaration(self) -> str:
        """String representation of the full declaration line"""

        attribute_parts = copy.copy(self.attribs)
        attribute_parts.insert(0, self.permission)
        if self.deferred:
            attribute_parts.insert(1, "deferred")
        attributes = ", ".join(attribute_parts)
        return f"{self.binding_type}, {attributes}"

    @property
    def num_lines(self) -> int:
        result = 0
        for binding in self.bindings:
            if isinstance(binding, FortranProcedure):
                result += binding.num_lines
        return result

    def correlate(self, project):
        self.all_procs = self.parent.all_procs

        if self.proto:
            proto_lower = self.proto.lower()
            if proto_lower in self.all_procs:
                self.proto = self.all_procs[proto_lower]
                self.protomatch = True
            elif proto_lower in self.parent.all_absinterfaces:
                self.proto = self.parent.all_absinterfaces[proto_lower]
                self.protomatch = True

        if self.generic:
            parent_boundprocs = {
                proc.name.lower(): proc for proc in self.parent.boundprocs if proc
            }

            for i, binding in enumerate(self.bindings):
                binding_name = getattr(binding, "name", binding).lower()
                with suppress(KeyError):
                    self.bindings[i] = parent_boundprocs[binding_name]

        elif not self.deferred:
            for i in range(len(self.bindings)):
                with suppress(KeyError):
                    self.bindings[i] = self.all_procs[self.bindings[i].lower()]
                    self.bindings[i].binding = self

        self.sort_components()

    def __repr__(self):
        return f"FortranBoundProcedure('{self.name}', permission='{self.permission}')"


class FortranModuleProcedureReference(FortranBase):
    """Reference to a module procedure whose interface and
    implementation are both defined elsewhere

    For example, this class represents the reference to ``fft_1d`` in
    a generic interface::

        interface fft
            module procedure fft_1d
            module procedure fft_2d
        end interface fft

    while ``fft_1d`` itself may be represented by either a
    `FortranSubroutine` or `FortranFunction`, or by the combination of
    `FortranModuleProcedureInterface` and `FortranModuleProcedureImplementation`

    """

    obj = "moduleprocedure"

    def __init__(self, name, parent=None, inherited_permission=None):
        if inherited_permission is not None:
            self.permission = inherited_permission.lower()
        else:
            self.permission = None
        self.parent = parent
        if self.parent:
            self.parobj = self.parent.obj
            self.settings = self.parent.settings
        else:
            self.parobj = None
            self.settings = None
        self.base_url = pathlib.Path(
            self.settings.project_url if self.settings else "."
        )
        self.name = name
        self.procedure = None
        self.doc_list = []
        self.hierarchy = self._make_hierarchy()
        self.read_metadata()
        self.source_file._to_be_markdowned.append(self)


class FortranBlockData(FortranContainer):
    """
    An object representing a block-data unit. Now obsolete due to modules,
    block data units allowed variables held in common blocks to be initialized
    outside of an executing program unit.
    """

    def _initialize(self, line):
        self.name = line.group(1)
        if not self.name:
            self.name = "<em>unnamed</em>"
        self.uses = []
        self.variables = []
        self.types = []
        self.common = []
        self.visible = True
        self.attr_dict = defaultdict(list)
        self.param_dict = {}

    def correlate(self, project):

        self.io_tracker.report()
        self.process_attribs()
        # Add procedures, interfaces and types from parent to our lists
        self.all_types = {}
        for dt in self.types:
            self.all_types[dt.name.lower()] = dt
        self.all_vars = {}
        for var in self.variables:
            self.all_vars[var.name.lower()] = var
        self.all_absinterfaces = {}
        self.all_procs = {}
        self.all_vars_ug = {}

        # Add procedures and types from USED modules to our lists
        for mod, extra in self.uses:
            if isinstance(mod, str):
                continue
            procs, absints, types, variables = mod.get_used_entities(extra)
            self.all_procs.update(procs)
            self.all_absinterfaces.update(absints)
            self.all_types.update(types)
            self.all_vars.update(variables)
        self.uses = [m[0] for m in self.uses]


        typelist = {}
        for dtype in self.types:
            if dtype.extends and dtype.extends.lower() in self.all_types:
                dtype.extends = self.all_types[dtype.extends.lower()]
                typelist[dtype] = set([dtype.extends])
            else:
                typelist[dtype] = set([])
        typeorder = toposort.toposort_flatten(typelist)

        for dtype in typeorder:
            dtype.visible = True
            if dtype in self.types:
                dtype.correlate(project)
        for var in self.variables:
            var.correlate(project)
        for com in self.common:
            com.correlate(project)

        self.sort_components()

    def prune(self):
        self.types = self.filter_display(self.types)
        self.variables = self.filter_display(self.variables)
        for dtype in self.types:
            dtype.visible = True
            dtype.prune()

    def _cleanup(self):
        # finish any half‑open sessions and emit their reports
        self.io_tracker.finalize()
        self.io_tracker.report()

        self.process_attribs()

    def process_attribs(self):
        for item in self.types:
            for attr in self.attr_dict[item.name.lower()]:
                if attr in ("public", "private", "protected"):
                    item.permission = attr
                elif attr[0:4] == "bind":
                    if hasattr(item, "bindC"):
                        item.bindC = attr[5:-1]
                    elif getattr(item, "procedure", None):
                        item.procedure.bindC = attr[5:-1]
                    else:
                        item.attribs.append(attr[5:-1])
        for var in self.variables:
            for attr in self.attr_dict[var.name.lower()]:
                if attr in ("public", "private", "protected"):
                    var.permission = attr
                elif attr[0:6] == "intent":
                    var.intent = attr[7:-1]
                elif DIM_RE.match(attr) and (
                    "pointer" in attr or "allocatable" in attr
                ):
                    i = attr.index("(")
                    var.attribs.append(attr[0:i])
                    var.dimension = attr[i:]
                elif attr == "parameter":
                    var.attribs.append(attr)
                    var.initial = self.param_dict[var.name.lower()]
                else:
                    var.attribs.append(attr)
        if hasattr(self, 'attr_dict'):
            del self.attr_dict


class FortranCommon(FortranBase):
    """
    An object representing a common block. This is a legacy feature.
    """

    def _initialize(self, line: re.Match) -> None:
        self.name = line.group(1)
        if not self.name:
            self.name = ""
        self.other_uses: List[FortranCommon] = []
        self.variables = [v.strip() for v in ford.utils.paren_split(",", line.group(2))]
        self.visible = True

    def correlate(self, project):
        for i in range(len(self.variables)):
            if self.variables[i] in self.parent.all_vars:
                self.variables[i] = self.parent.all_vars[self.variables[i]]
                with suppress(ValueError):
                    self.parent.variables.remove(self.variables[i])
            else:
                self.variables[i] = FortranVariable(
                    self.variables[i], implicit_type(self.variables[i]), self, doc=""
                )

        if self.name in project.common:
            self.other_uses = project.common[self.name]
            self.other_uses.append(self)
        else:
            lst = [self]
            project.common[self.name] = lst
            self.other_uses = lst

        self.sort_components()

    def _cleanup(self) -> None:
        # finish any half‑open sessions and emit their reports
        self.io_tracker.finalize()
        self.io_tracker.report()

        # now apply attribute processing if needed
        self.process_attribs()


class FortranSpoof:
    """
    A dummy-type which is used to represent arguments, interfaces, type-bound
    procedures, etc. which lack a corresponding variable or implementation.
    """

    IS_SPOOF = True

    def __init__(self, name, parent=None, obj="ITEM"):
        self.name = name
        self.parent = parent
        self.obj = obj
        if self.parent.settings.warn:
            warn(
                f"{self.obj} '{self.name}' in {self.parent.obj} '{self.parent.name}' could not be matched to "
                f"corresponding item in code (file {self.filename})"
            )

    def __getitem__(self, key):
        return []

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False

    def __getattr__(self, name):
        return []

    def __str__(self):
        return self.name


class GenericSource(FortranBase):
    """
    Represent a non-Fortran source file. The contents of the file will
    not be analyzed, but documentation can be extracted.
    """

    def __init__(self, filename: PathLike, settings: ProjectSettings):
        self.obj = "sourcefile"
        self.parobj = None
        self.parent = None
        self.hierarchy = []
        self.settings = settings
        self.base_url = self.settings.project_url
        self.num_lines = 0
        filename = pathlib.Path(filename)
        extra_filetypes = settings.extra_filetypes[str(filename.suffix)[1:]]

        self.path = filename
        self.name = self.path.name
        self.raw_src = self.path.read_text(encoding=settings.encoding)
        # TODO: Get line numbers to display properly
        if extra_filetypes.lexer is None:
            lexer = guess_lexer_for_filename(self.name, self.raw_src)
        else:
            import pygments.lexers

            lexer = getattr(pygments.lexers, extra_filetypes.lexer)
        self.src = highlight(
            self.raw_src,
            lexer,
            HtmlFormatter(lineanchors="ln", cssclass="hl codehilite"),
        )

        self.comment = extra_filetypes.comment
        comchar = re.escape(extra_filetypes.comment)
        self.com_re = re.compile(
            r"^((?!{0}|[\"']).|(\'[^']*')|(\"[^\"]*\"))*({0}.*)$".format(comchar)
        )

        docmark = settings.docmark
        predocmark = settings.predocmark
        docmark_alt = settings.docmark_alt
        predocmark_alt = settings.predocmark_alt

        docmark_re_bit = (
            f"(?:{re.escape(settings.docmark)}|{re.escape(settings.predocmark)})"
            if settings.predocmark
            else re.escape(settings.docmark)
        )

        self.doc_re = re.compile(
            r"^((?!{0}|[\"']).|('[^']*')|(\"[^\"]*\"))*({0}{1}.*)$".format(
                comchar, docmark_re_bit
            )
        )

        if _docmark_alt := self._docmark_alt(settings):
            self.doc_alt_re: Optional[re.Pattern] = re.compile(
                r"^((?!{0}|[\"']).|('[^']*')|(\"[^\"]*\"))*({0}{1}.*)$".format(
                    comchar, _docmark_alt
                )
            )
        else:
            self.doc_alt_re = None

        self.doc_comment = extra_filetypes.comment + docmark
        self.doc_comment_alt = extra_filetypes.comment + docmark_alt
        self.predoc_comment = extra_filetypes.comment + predocmark
        self.predoc_comment_alt = extra_filetypes.comment + predocmark_alt

        self.parse_file(settings.encoding)

        self.read_metadata()

    @property
    def markdownable_items(self):
        return [self]

    @staticmethod
    def _docmark_alt(settings: ProjectSettings) -> str:
        if settings.docmark_alt and settings.predocmark_alt:
            return f"(?:{re.escape(settings.docmark_alt)}|{re.escape(settings.predocmark_alt)})"
        elif settings.docmark_alt:
            return re.escape(settings.docmark_alt)
        elif settings.predocmark_alt:
            return re.escape(settings.predocmark_alt)
        else:
            return ""

    def parse_file(self, encoding: str = "utf-8"):
        self.doc_list = []
        prevdoc = False
        docalt = False
        with open(self.path, "r", encoding=encoding) as lines:
            for line in lines:
                line = line.strip()
                if self.doc_alt_re and (match := self.doc_alt_re.match(line)):
                    prevdoc = True
                    docalt = True
                    self.doc_list.append(
                        remove_prefixes(
                            match.group(4),
                            self.doc_comment_alt,
                            self.predoc_comment_alt,
                        )
                    )
                    continue

                if match := self.doc_re.match(line):
                    prevdoc = True
                    if docalt:
                        docalt = False

                    self.doc_list.append(
                        remove_prefixes(
                            match.group(4), self.doc_comment, self.predoc_comment
                        )
                    )
                    continue

                if match := self.com_re.match(line):
                    if docalt:
                        if match.start(4) == 0:
                            self.doc_list.append(
                                remove_prefixes(match.group(4), self.comment)
                            )
                        else:
                            docalt = False
                    elif prevdoc:
                        prevdoc = False
                        self.doc_list.append("")
                    continue

                # if not including any comment...
                if prevdoc:
                    self.doc_list.append("")
                    prevdoc = False
                docalt = False

    def lines_description(self, total, total_all=0):
        return ""


def remove_prefixes(string: str, prefix1: str, prefix2: Optional[str] = None) -> str:
    if sys.version_info >= (3, 9):
        string = string.removeprefix(prefix1)
        if prefix2:
            string = string.removeprefix(prefix2)
        return string.strip()

    if string.startswith(prefix1):
        string = string[len(prefix1) :]
    if prefix2 and string.startswith(prefix2):
        string = string[len(prefix2) :]
    return string.strip()


_can_have_contains = (
    FortranModule,
    FortranProgram,
    FortranProcedure,
    FortranType,
    FortranSubmodule,
    FortranModuleProcedureImplementation,
)


def remove_kind_suffix(literal, is_character: bool = False):
    """Return the literal without the kind suffix of a numerical literal,
    or the kind prefix of a character literal"""

    kind_re = CHAR_KIND_SUFFIX_RE if is_character else KIND_SUFFIX_RE
    kind_suffix = kind_re.match(literal)
    if kind_suffix:
        return kind_suffix.group("initial")
    return literal


def line_to_variables(source, line, inherit_permission, parent):
    """
    Returns a list of variables declared in the provided line of code. The
    line of code should be provided as a string.
    """
    parsed_type = parse_type(line, parent.strings, parent.settings.extra_vartypes)
    attribs = []
    intent = ""
    optional = False
    permission = inherit_permission
    parameter = False

    if attribmatch := ATTRIBSPLIT_RE.match(parsed_type.rest):
        attribstr = attribmatch.group(1).strip()
        declarestr = attribmatch.group(2).strip()
        tmp_attribs = [attr.strip() for attr in ford.utils.paren_split(",", attribstr)]
        for tmp_attrib in tmp_attribs:
            # Lowercase and remove whitespace so checking intent is cleaner
            tmp_attrib_lower = tmp_attrib.lower().replace(" ", "")

            if tmp_attrib_lower in ["public", "private", "protected"]:
                permission = tmp_attrib_lower
            elif tmp_attrib_lower == "optional":
                optional = True
            elif tmp_attrib_lower == "parameter":
                parameter = True
            elif tmp_attrib_lower == "intent(in)":
                intent = "in"
            elif tmp_attrib_lower == "intent(out)":
                intent = "out"
            elif tmp_attrib_lower == "intent(inout)":
                intent = "inout"
            else:
                attribs.append(tmp_attrib)
    else:
        declarestr = ATTRIBSPLIT2_RE.match(parsed_type.rest).group(2)
    declarations = ford.utils.paren_split(",", declarestr)

    doc = read_docstring(source, parent.settings.docmark)

    varlist = []
    for dec in declarations:
        dec = re.sub(" ", "", dec)
        split = ford.utils.paren_split("=", dec)
        if len(split) > 1:
            name = split[0]
            points = split[1][0] == ">"
            if points:
                initial = split[1][1:]
            else:
                initial = split[1]
        else:
            name = dec.strip()
            initial = None
            points = False

        if initial:
            initial = COMMA_RE.sub(", ", initial)
            # TODO: pull out into standalone function?
            search_from = 0
            while quote := QUOTES_RE.search(initial[search_from:]):
                num = int(quote.group()[1:-1])
                # Replace multiple consecutive spaces with non-breaking spaces
                # so they don't get combined in the html
                string = NBSP_RE.sub("\xa0", parent.strings[num])
                string = string.replace("\\", "\\\\")
                initial = initial[0:search_from] + QUOTES_RE.sub(
                    string, initial[search_from:], count=1
                )
                search_from += QUOTES_RE.search(initial[search_from:]).end(0)

        varlist.append(
            FortranVariable(
                name,
                parsed_type.vartype,
                parent,
                copy.copy(attribs),
                intent,
                optional,
                permission,
                parameter,
                parsed_type.kind,
                parsed_type.strlen,
                parsed_type.proto,
                doc,
                points,
                initial,
                line_number=getattr(source, 'line_number', None),
            )
        )

    return varlist


_EXTRA_TYPES_RE_CACHE: Dict[Tuple[str, ...], re.Pattern] = {}


@dataclass
class ParsedType:
    vartype: str
    rest: str
    kind: Optional[str] = None
    strlen: Optional[str] = None
    proto: Union[None, str, List[str]] = None


def parse_type(
    string: str, capture_strings: List[str], extra_vartypes: Sequence[str]
) -> ParsedType:
    """
    Gets variable type, kind, length, and/or derived-type attributes from a
    variable declaration.
    """
    extra_vartypes = tuple(extra_vartypes)
    try:
        var_type_re = _EXTRA_TYPES_RE_CACHE[extra_vartypes]
    except KeyError:
        var_type_re = re.compile(
            "|".join((VAR_TYPE_STRING, *extra_vartypes)), re.IGNORECASE
        )
        _EXTRA_TYPES_RE_CACHE[extra_vartypes] = var_type_re

    if not (match := var_type_re.match(string)):
        raise ValueError(f"Invalid variable declaration: {string}")

    vartype = match.group().lower()
    if DOUBLE_PREC_RE.match(vartype):
        vartype = "double precision"
    if DOUBLE_CMPLX_RE.match(vartype):
        vartype = "double complex"
    rest = string[match.end() :].strip()
    kindstr = ford.utils.get_parens(rest)
    rest = rest[len(kindstr) :].strip()

    if (
        len(kindstr) < 3
        and vartype not in ["type", "class", "character"]
        and not kindstr.startswith("*")
    ):
        return ParsedType(vartype, rest)

    match = VARKIND_RE.search(kindstr)
    if not match:
        if vartype == "character":
            # This is a bare `character` declaration with no parameters
            return ParsedType(vartype, rest, strlen="1")

        raise ValueError(f"Bad declaration of variable type '{vartype}': {string}")

    if match.group(1):
        star = False
        args = match.group(1).strip()
    else:
        star = True
        args = match.group(2).strip()
        if args.startswith("("):
            args = args[1:-1].strip()

    args = re.sub(r"\s", "", args)
    if vartype in ["type", "class", "procedure"]:
        if not (proto_match := PROTO_RE.match(args)):
            raise ValueError(
                f"Bad type, class, or procedure prototype specification: {args}"
            )
        proto = list(proto_match.groups())
        if not proto[1]:
            proto[1] = ""
        return ParsedType(vartype, rest, proto=proto)

    if vartype == "character":
        if star:
            return ParsedType(vartype, rest, strlen=args)

        args = args.split(",")

        if len(args) > 2:
            raise ValueError(
                f"Bad declaration of `character`, too many parameters: '{string}'"
            )

        # `character` has two parameters: `len` and `kind`.
        # If the parameter names are present, they can be in any order.
        # If they're missing, `len` must be first and `kind` second.
        # If there are no parameters at all, this is handled above.

        length = None
        kind = None
        for arg in args:
            if length is None and (length_match := LEN_RE.match(arg)):
                length = length_match.group(1) or length_match.group(2)
                continue

            if kind is None and (kind_match := KIND_RE.match(arg)):
                kind = kind_match.group(1)
                if match := QUOTES_RE.search(kind):
                    num = int(match.group()[1:-1])
                    kind = QUOTES_RE.sub(capture_strings[num], kind)
                continue

            if length is None:
                length = arg
                continue

            if kind is None:
                kind = arg

        # Handle default values
        if length is None:
            length = "1"

        return ParsedType(vartype, rest, kind=kind, strlen=length)

    kind = KIND_RE.match(args)
    kind = kind.group(1) if kind else args
    return ParsedType(vartype, rest, kind=kind)


def get_mod_procs(
    source: FortranReader, names: str, parent: FortranInterface
) -> List[FortranModuleProcedureReference]:
    """Get module procedures from an interface"""
    retlist = [
        FortranModuleProcedureReference(item, parent, parent.permission)
        for item in re.split(r"\s*,\s*", names)
    ]

    retlist[-1].doc_list = read_docstring(source, parent.settings.docmark)
    return retlist


class NameSelector:
    """
    Object which tracks what names have been provided for different
    entities in Fortran code. It will provide an identifier which is
    guaranteed to be unique. This identifier can then me used as a
    filename for the documentation of that entity.
    """

    def __init__(self):
        self._items = {}
        self._counts = {}

    def get_name(self, item):
        """
        Return the name for this item registered with this NameSelector.
        If no name has previously been registered, then generate a new
        one.
        """
        if not isinstance(item, ford.sourceform.FortranBase):
            raise TypeError(f"'{item}' is not of a type derived from FortranBase")

        if item in self._items:
            return self._items[item]
        else:
            if item.get_dir() not in self._counts:
                self._counts[item.get_dir()] = {}
            if item.name in self._counts[item.get_dir()]:
                num = self._counts[item.get_dir()][item.name] + 1
            else:
                num = 1
            self._counts[item.get_dir()][item.name] = num
            name = item.name.lower()
            for symbol, replacement in {
                "<": "lt",
                ">": "gt",
                "/": "SLASH",
                "*": "ASTERISK",
            }.items():
                name = name.replace(symbol, replacement)
            if name == "":
                name = "__unnamed__"
            if num > 1:
                name = name + "~" + str(num)
            self._items[item] = name
            return name


namelist = NameSelector()


class ExternalModule(FortranModule):
    _project_list = "extModules"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "module"
        self.uses = []
        self.pub_procs = {}
        self.pub_absints = {}
        self.pub_types = {}
        self.pub_vars = {}


class ExternalFunction(FortranFunction):
    _project_list = "extProcedures"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "proc"


class ExternalSubroutine(FortranSubroutine):
    _project_list = "extProcedures"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "proc"


class ExternalInterface(FortranInterface):
    _project_list = "extProcedures"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "proc"


class ExternalBoundProcedure(FortranBoundProcedure):
    _project_list = "extProcedures"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "proc"
        self.bindings = []
        self.attribs = []
        self.deferred = False
        self.generic = False


class ExternalType(FortranType):
    _project_list = "extTypes"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "type"
        self.boundprocs = []
        self.variables = []


class ExternalVariable(FortranVariable):
    _project_list = "extVariables"

    def __init__(self, name: str, url: str = "", parent=None):
        self.name = name
        self.external_url = url
        self.parent = parent
        self.obj = "variable"
        self.kind = None
        self.strlen = None
        self.proto = None


class ExternalSubmodule(FortranSubmodule):
    def __init__(self, name: str):
        self.name = name
        self.url = ""
        self.uses = []
        self.parent_submodule = None
        self.ancestor_module = ExternalModule("Parent module")
        self.external_url = ""


class ExternalProgram(FortranProgram):
    def __init__(self, name: str):
        self.name = name
        self.url = ""
        self.uses = []
        self.calls = []
        self.external_url = ""


class ExternalSourceFile(FortranSourceFile):
    def __init__(self, name: str):
        self.name = name
        self.url = ""
        self.modules = []
        self.submodules = []
        self.functions = []
        self.subroutines = []
        self.programs = []
        self.blockdata = []
        self.external_url = ""