#!/usr/bin/env python3
"""Compare input/output file usage and schemas between two Ford doc outputs.

Covers all IO categories: input, output, input_output, unknown.
For each common file it reports:
  - added / removed / reordered I/O operations (read & write)
  - file-schema row diffs (variable name, type, position, condition)
  - derived-type field changes (resolved from Fortran source trees)

Usage
-----
python tools/compare_iofiles.py \\
    --old-docs  older_swat_docs \\
    --new-docs  swatplus_docs   \\
    --old-src   swatplus_src_61 \\
    --new-src   src             \\
    --out       compare_iofiles.json \\
    --csv       compare_iofiles_summary.csv \\
    --schema-csv       compare_iofiles_schema.csv \\
    --schema-csv-lite  compare_iofiles_schema_lite.csv \\
    --types-csv        compare_iofiles_types.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# HTML section-id  →  iofile sub-directory  (the four FORD categories)
# ---------------------------------------------------------------------------
CATEGORIES: Dict[str, str] = {
    "input":         "input",
    "output":        "output",
    "input_output":  "input_output",
    "unknown":       "unknown",
}

SECTION_ID_MAP: Dict[str, str] = {
    # Use id="..." anchors so that "output-files-section" does NOT false-match
    # inside "input-output-files-section".
    "input":        'id="input-files-section"',
    "output":       'id="output-files-section"',
    "input_output": 'id="input-output-files-section"',
    "unknown":      'id="unknown-files-section"',
}

TAG_RE  = re.compile(r"<[^>]+>")
CODE_RE = re.compile(r"<code>(.*?)</code>", re.IGNORECASE | re.DOTALL)
TD_RE   = re.compile(r"<td[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)

# Matches a link inside an iofile section:  href="../iofile/<cat>/<slug>.html">Display name<
LINK_RE = re.compile(
    r'href="\.\./iofile/(?P<cat>[^/]+)/(?P<slug>[^"]+)"[^>]*>(?P<name>[^<]+)<',
    re.IGNORECASE,
)

# Procedure-header in an iofile detail page  (same regex as original tool)
PROC_HEADER_RE = re.compile(
    r"<h3[^>]*>\s*<i[^>]*></i>\s*([^<\n]+)\s*<small[^>]*>\s*\(from\s*<a[^>]*href='../../sourcefile/([^']+)'",
    re.IGNORECASE | re.DOTALL,
)

READ_RE  = re.compile(r"^read\s*\([^)]*\)\s*(.*)", re.IGNORECASE)
WRITE_RE = re.compile(r"^write\s*\([^)]*\)\s*(.*)", re.IGNORECASE)

# Fortran source patterns
TYPE_RE     = re.compile(r"^\s*type\s*(::)?\s*(?P<name>\w+)\b", re.IGNORECASE)
END_TYPE_RE = re.compile(r"^\s*end\s*type\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Simple data structures
# ---------------------------------------------------------------------------

@dataclass
class IoOp:
    line:      str
    operation: str
    raw:       str


@dataclass
class FileEntry:
    """One IO-file as referenced from iofiles.html."""
    name:  str   # display name  (e.g. "aquifer.aqu")
    slug:  str   # HTML filename  (e.g. "aquifer_aqu.html")
    cat:   str   # category key   (e.g. "input")


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def strip_tags(text: str) -> str:
    return TAG_RE.sub("", text).strip()


# ---------------------------------------------------------------------------
# Parse the master iofiles.html list
# ---------------------------------------------------------------------------

def parse_iofiles_list(iofiles_html: str) -> Dict[str, Dict[str, FileEntry]]:
    """Return {category: {display_name: FileEntry}}."""
    text      = read_text(iofiles_html)
    result: Dict[str, Dict[str, FileEntry]] = {cat: {} for cat in CATEGORIES}

    current_cat: Optional[str] = None
    # Walk through section markers + links line by line
    for line in text.splitlines():
        for cat_key, section_id in SECTION_ID_MAP.items():
            if section_id in line:
                current_cat = cat_key
                break
        if current_cat is None:
            continue
        for m in LINK_RE.finditer(line):
            cat_dir = m.group("cat")
            slug    = m.group("slug")
            name    = m.group("name").strip()
            # Confirm category matches where we are in the document
            for cat_key, cat_dir_exp in CATEGORIES.items():
                if cat_dir == cat_dir_exp and cat_key == current_cat:
                    result[current_cat][name] = FileEntry(name=name, slug=slug, cat=cat_key)
    return result


# ---------------------------------------------------------------------------
# Table parser (reusable for any named <h4> table)
# ---------------------------------------------------------------------------

class SectionTableParser(HTMLParser):
    """Parse the first <table> that follows an <h4>target_h4</h4>."""

    def __init__(self, target_h4: str) -> None:
        super().__init__()
        self.target_h4       = target_h4
        self.in_h4           = False
        self.h4_text         = ""
        self.capture_next    = False
        self.in_table        = False
        self.in_tr           = False
        self.in_cell         = False
        self.headers: List[str]        = []
        self.rows:    List[List[str]]  = []
        self._cur_row: List[str]       = []
        self._cell   = ""
        self._done   = False

    def handle_starttag(self, tag: str, attrs):
        if self._done:
            return
        if tag == "h4":
            self.in_h4   = True
            self.h4_text = ""
        elif tag == "table" and self.capture_next:
            self.in_table     = True
            self.capture_next = False
        elif self.in_table and tag == "tr":
            self.in_tr    = True
            self._cur_row = []
        elif self.in_table and self.in_tr and tag in ("td", "th"):
            self.in_cell = True
            self._cell   = ""

    def handle_endtag(self, tag: str):
        if self._done:
            return
        if tag == "h4" and self.in_h4:
            title = " ".join(self.h4_text.split())
            if title == self.target_h4:
                self.capture_next = True
            self.in_h4   = False
            self.h4_text = ""
        elif tag in ("td", "th") and self.in_cell:
            self._cur_row.append(" ".join(self._cell.split()))
            self.in_cell = False
            self._cell   = ""
        elif tag == "tr" and self.in_tr:
            if self._cur_row:
                if not self.headers:
                    self.headers = self._cur_row
                else:
                    self.rows.append(self._cur_row)
            self.in_tr    = False
            self._cur_row = []
        elif tag == "table" and self.in_table:
            self.in_table = False
            self._done    = True   # stop after first matching table

    def handle_data(self, data: str):
        if self.in_h4:
            self.h4_text += data
        if self.in_cell:
            self._cell += data


def parse_section_table(html: str, title: str) -> Dict:
    parser = SectionTableParser(title)
    parser.feed(html)
    return {"headers": parser.headers, "rows": parser.rows}


def rows_to_dicts(headers: List[str], rows: List[List[str]]) -> List[Dict[str, str]]:
    return [
        {headers[i]: (row[i] if i < len(row) else "")
         for i in range(len(headers))}
        for row in rows
    ]


# ---------------------------------------------------------------------------
# IO operations from detail pages
# ---------------------------------------------------------------------------

def _parse_io_table(html: str) -> List[IoOp]:
    """Extract I/O operations table from an iofile detail page."""
    p = SectionTableParser("I/O Operations")
    p.feed(html)
    ops: List[IoOp] = []
    for row in p.rows:
        if len(row) < 3:
            continue
        raw_cell = row[2]
        code_m   = CODE_RE.search(raw_cell)
        raw      = strip_tags(code_m.group(1)) if code_m else strip_tags(raw_cell)
        ops.append(IoOp(line=row[0], operation=row[1], raw=raw))
    return ops


def extract_io_sequence(ops: List[IoOp]) -> List[str]:
    """Return list of read/write statement tails in order."""
    result = []
    for op in ops:
        op_lower = op.operation.lower()
        m = None
        if op_lower == "read":
            m = READ_RE.match(op.raw.strip())
        elif op_lower == "write":
            m = WRITE_RE.match(op.raw.strip())
        if m:
            tail = m.group(1).strip()
            if tail:
                result.append(f"{op.operation.lower()}: {tail}")
    return result


def extract_read_sequence(ops: List[IoOp]) -> List[str]:
    result = []
    for op in ops:
        if op.operation.lower() != "read":
            continue
        m = READ_RE.match(op.raw.strip())
        if m and m.group(1).strip():
            result.append(m.group(1).strip())
    return result


def extract_write_sequence(ops: List[IoOp]) -> List[str]:
    result = []
    for op in ops:
        if op.operation.lower() != "write":
            continue
        m = WRITE_RE.match(op.raw.strip())
        if m and m.group(1).strip():
            result.append(m.group(1).strip())
    return result


def parse_proc_io_ops(html: str) -> List[Tuple[str, List[IoOp]]]:
    """Return [(proc_name, [IoOp, ...]), ...] extracted from a detail page."""
    all_ops = _parse_io_table(html)
    # The page may have multiple proc sections; for sequence comparison we
    # collapse them into one ordered list.  For names we use the header regex.
    names = [n.strip() for n, _ in PROC_HEADER_RE.findall(html)]
    return names, all_ops


# ---------------------------------------------------------------------------
# File-schema comparison
# ---------------------------------------------------------------------------

IGNORED_SCHEMA_COLS = {"Default", "Units", "Description", "Default Value / Initial"}


def compare_file_schema(
    old_table: Dict, new_table: Dict
) -> Dict:
    old_headers = old_table.get("headers", [])
    new_headers = new_table.get("headers", [])
    old_dicts   = rows_to_dicts(old_headers, old_table.get("rows", []))
    new_dicts   = rows_to_dicts(new_headers, new_table.get("rows", []))

    def key(row: Dict[str, str]) -> Tuple[str, str, str]:
        return (
            row.get("Line in File", ""),
            row.get("Position in File", ""),
            row.get("Component", ""),
        )

    old_map = {key(r): r for r in old_dicts}
    new_map = {key(r): r for r in new_dicts}
    all_keys = sorted(set(old_map) | set(new_map))

    diffs: List[Dict] = []
    for k in all_keys:
        o = old_map.get(k)
        n = new_map.get(k)
        if o != n:
            diffs.append({"key": k, "old": o, "new": n})

    lite_diffs: List[Dict] = []
    for k in all_keys:
        o = {c: v for c, v in (old_map.get(k) or {}).items()
             if c not in IGNORED_SCHEMA_COLS}
        n = {c: v for c, v in (new_map.get(k) or {}).items()
             if c not in IGNORED_SCHEMA_COLS}
        if o != n:
            lite_diffs.append({"key": k, "old": o or None, "new": n or None})

    return {
        "headers": old_headers or new_headers,
        "old":  old_dicts,
        "new":  new_dicts,
        "diff": diffs,
        "diff_lite": lite_diffs,
    }


# ---------------------------------------------------------------------------
# Fortran derived-type extraction
# ---------------------------------------------------------------------------

def find_type_block(root: str, type_name: str) -> Optional[str]:
    pattern = re.compile(
        rf"^\s*type\s*(::)?\s*{re.escape(type_name)}\b", re.IGNORECASE
    )
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if not fname.lower().endswith(".f90"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    in_block = False
                    lines: List[str] = []
                    for ln in fh:
                        if not in_block and pattern.search(ln):
                            in_block = True
                            lines.append(ln)
                        elif in_block:
                            lines.append(ln)
                            if END_TYPE_RE.search(ln):
                                return "".join(lines)
            except OSError:
                continue
    return None


def extract_type_field_entries(block: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for ln in block.splitlines():
        if "::" not in ln:
            continue
        cleaned = ln.split("!", 1)[0].strip()
        if not cleaned or re.search(r"\bprocedure\b", cleaned, re.IGNORECASE):
            continue
        type_part, name_part = [p.strip() for p in cleaned.split("::", 1)]
        for raw_name in name_part.split(","):
            name = raw_name.strip().split("(")[0].strip()
            if name:
                entries.append({"name": name, "type": type_part})
    return entries


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def compare_lists(old: List[str], new: List[str]) -> Dict[str, List[str]]:
    os_, ns_ = set(old), set(new)
    return {
        "added":   sorted(ns_ - os_),
        "removed": sorted(os_ - ns_),
        "common":  sorted(os_ & ns_),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compare input/output file usage and schemas between two Ford doc outputs."
    )
    ap.add_argument("--old-docs",  required=True, help="Older Ford docs output directory")
    ap.add_argument("--new-docs",  required=True, help="Newer Ford docs output directory")
    ap.add_argument("--old-src",   required=True, help="Older Fortran source tree")
    ap.add_argument("--new-src",   required=True, help="Newer Fortran source tree")
    ap.add_argument("--out",       required=True, help="JSON report output path")
    ap.add_argument("--csv",       help="CSV summary (one row per file)")
    ap.add_argument("--schema-csv",      help="Full per-row schema diff CSV")
    ap.add_argument("--schema-csv-lite", help="Schema diff CSV (no defaults/units/description)")
    ap.add_argument("--types-csv", help="Derived-type change summary CSV")
    ap.add_argument(
        "--categories",
        nargs="+",
        choices=list(CATEGORIES.keys()),
        default=list(CATEGORIES.keys()),
        help="Categories to compare (default: all)",
    )
    args = ap.parse_args()

    old_iofiles = os.path.join(args.old_docs, "lists", "iofiles.html")
    new_iofiles = os.path.join(args.new_docs, "lists", "iofiles.html")

    old_all = parse_iofiles_list(old_iofiles)
    new_all = parse_iofiles_list(new_iofiles)

    report: Dict = {
        "summary": {
            "old_docs": args.old_docs,
            "new_docs": args.new_docs,
            "old_src":  args.old_src,
            "new_src":  args.new_src,
        },
        "categories": {},
        "files": {},
        "types": {},
    }

    all_type_names: set = set()

    for cat in args.categories:
        old_map = old_all.get(cat, {})
        new_map = new_all.get(cat, {})

        diff = compare_lists(list(old_map.keys()), list(new_map.keys()))
        report["categories"][cat] = {
            "added":   diff["added"],
            "removed": diff["removed"],
            "common":  [],
        }

        print(f"\n[{cat}]  added={len(diff['added'])}  removed={len(diff['removed'])}  common={len(diff['common'])}")

        for name in diff["common"]:
            old_entry = old_map[name]
            new_entry = new_map[name]
            old_page  = os.path.join(args.old_docs, "iofile", cat, old_entry.slug)
            new_page  = os.path.join(args.new_docs, "iofile", cat, new_entry.slug)

            if not os.path.isfile(old_page) or not os.path.isfile(new_page):
                print(f"  WARNING: missing page for {name}, skipping")
                continue

            old_html = read_text(old_page)
            new_html = read_text(new_page)

            old_proc_names, old_ops = parse_proc_io_ops(old_html)
            new_proc_names, new_ops = parse_proc_io_ops(new_html)

            proc_diff     = compare_lists(old_proc_names, new_proc_names)
            old_io_seq    = extract_io_sequence(old_ops)
            new_io_seq    = extract_io_sequence(new_ops)
            old_read_seq  = extract_read_sequence(old_ops)
            new_read_seq  = extract_read_sequence(new_ops)
            old_write_seq = extract_write_sequence(old_ops)
            new_write_seq = extract_write_sequence(new_ops)

            schema_diff = compare_file_schema(
                parse_section_table(old_html, "File Schema"),
                parse_section_table(new_html, "File Schema"),
            )

            # Collect type names from "Variables Written"/"File Schema" TYPE column
            schema_types = sorted({
                row.get("TYPE", "").strip()
                for row in schema_diff["old"] + schema_diff["new"]
                if row.get("TYPE") and row.get("TYPE") not in ("-", "")
            })
            all_type_names.update(schema_types)

            key = f"{cat}::{name}"
            report["files"][key] = {
                "category":   cat,
                "name":       name,
                "procedures": proc_diff,
                "io_sequence": {
                    "old": old_io_seq,
                    "new": new_io_seq,
                },
                "read_sequence": {
                    "old": old_read_seq,
                    "new": new_read_seq,
                },
                "write_sequence": {
                    "old": old_write_seq,
                    "new": new_write_seq,
                },
                "file_schema":       schema_diff,
                "file_schema_types": schema_types,
                "procedures_list":   sorted(set(old_proc_names + new_proc_names)),
            }
            report["categories"][cat]["common"].append(name)

    # -----------------------------------------------------------------------
    # Resolve derived types from both source trees
    # -----------------------------------------------------------------------
    print(f"\nResolving {len(all_type_names)} derived types …")
    for type_name in sorted(all_type_names):
        old_block   = find_type_block(args.old_src, type_name)
        new_block   = find_type_block(args.new_src, type_name)
        old_entries = extract_type_field_entries(old_block) if old_block else []
        new_entries = extract_type_field_entries(new_block) if new_block else []
        report["types"][type_name] = {
            "old_entries": old_entries,
            "new_entries": new_entries,
        }

    # -----------------------------------------------------------------------
    # Write JSON
    # -----------------------------------------------------------------------
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"\nWrote JSON report: {args.out}")

    # -----------------------------------------------------------------------
    # Write CSV summary
    # -----------------------------------------------------------------------
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "category", "io_file", "status",
                "procedures_added", "procedures_removed",
                "read_sequence_changed", "write_sequence_changed",
                "io_sequence_changed", "file_schema_changed",
                "file_schema_lite_changed",
            ])
            # Added / removed rows from categories
            for cat in args.categories:
                cat_info = report["categories"][cat]
                added_set   = set(cat_info["added"])
                removed_set = set(cat_info["removed"])
                for name in cat_info["added"]:
                    writer.writerow([cat, name, "added", "", "", "", "", "", "", ""])
                for name in cat_info["removed"]:
                    writer.writerow([cat, name, "removed", "", "", "", "", "", "", ""])
            # Common files
            for key in sorted(report["files"].keys()):
                fe = report["files"][key]
                cat  = fe["category"]
                name = fe["name"]
                pd   = fe["procedures"]
                writer.writerow([
                    cat,
                    name,
                    "common",
                    ";".join(pd.get("added", [])),
                    ";".join(pd.get("removed", [])),
                    "Y" if fe["read_sequence"]["old"]  != fe["read_sequence"]["new"]  else "N",
                    "Y" if fe["write_sequence"]["old"] != fe["write_sequence"]["new"] else "N",
                    "Y" if fe["io_sequence"]["old"]    != fe["io_sequence"]["new"]    else "N",
                    "Y" if fe["file_schema"]["diff"]      else "N",
                    "Y" if fe["file_schema"]["diff_lite"] else "N",
                ])
        print(f"Wrote CSV summary: {args.csv}")

    # -----------------------------------------------------------------------
    # Write schema-diff CSVs
    # -----------------------------------------------------------------------
    def _write_schema_csv(path: str, diff_key: str):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "category", "io_file",
                "line_in_file", "position_in_file", "component",
                "old_row", "new_row",
            ])
            for key in sorted(report["files"].keys()):
                fe    = report["files"][key]
                cat   = fe["category"]
                name  = fe["name"]
                diffs = fe["file_schema"][diff_key]
                for d in diffs:
                    ln, pos, comp = d["key"]
                    writer.writerow([cat, name, ln, pos, comp,
                                     d.get("old"), d.get("new")])

    if args.schema_csv:
        _write_schema_csv(args.schema_csv, "diff")
        print(f"Wrote schema diff CSV: {args.schema_csv}")

    if args.schema_csv_lite:
        _write_schema_csv(args.schema_csv_lite, "diff_lite")
        print(f"Wrote schema diff CSV (lite): {args.schema_csv_lite}")

    # -----------------------------------------------------------------------
    # Write types CSV
    # -----------------------------------------------------------------------
    if args.types_csv:
        with open(args.types_csv, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "category", "io_file", "procedures",
                "derived_types", "derived_types_changed",
            ])
            for key in sorted(report["files"].keys()):
                fe    = report["files"][key]
                cat   = fe["category"]
                name  = fe["name"]
                types = fe.get("file_schema_types", [])
                changed = [
                    t for t in types
                    if report["types"].get(t, {}).get("old_entries")
                       != report["types"].get(t, {}).get("new_entries")
                ]
                writer.writerow([
                    cat,
                    name,
                    ";".join(fe.get("procedures_list", [])),
                    ";".join(types),
                    ";".join(changed),
                ])
        print(f"Wrote types CSV: {args.types_csv}")

    # -----------------------------------------------------------------------
    # Terminal summary
    # -----------------------------------------------------------------------
    print("\n=== Summary ===")
    for cat in args.categories:
        ci = report["categories"][cat]
        print(f"  {cat:15s}  added={len(ci['added']):3d}  "
              f"removed={len(ci['removed']):3d}  common={len(ci['common']):3d}")

    total_schema_changed = sum(
        1 for fe in report["files"].values()
        if fe["file_schema"]["diff_lite"]
    )
    total_io_changed = sum(
        1 for fe in report["files"].values()
        if fe["io_sequence"]["old"] != fe["io_sequence"]["new"]
    )
    print(f"\n  Files with I/O sequence changes : {total_io_changed}")
    print(f"  Files with schema changes       : {total_schema_changed}")
    print(f"  Derived types resolved          : {len(report['types'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
