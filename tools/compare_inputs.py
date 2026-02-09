#!/usr/bin/env python3
"""Compare input file usage and schemas between two Ford doc outputs and sources."""

from __future__ import annotations

import argparse
import json
import os
import re
import csv
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple


INPUT_SECTION_RE = re.compile(
    r"id=\"input-files-section\".*?</div>", re.IGNORECASE | re.DOTALL
)
INPUT_LINK_RE = re.compile(r"href=\"\.\./iofile/input/([^\"]+)\"[^>]*>([^<]+)<")

PROC_HEADER_RE = re.compile(
    r"<h3[^>]*>\s*<i[^>]*></i>\s*([^<\n]+)\s*<small[^>]*>\s*\(from\s*<a[^>]*href='../../sourcefile/([^']+)'",
    re.IGNORECASE | re.DOTALL,
)

FILENAME_TABLE_RE = re.compile(
    r"<h4>Filename</h4>\s*<table.*?>\s*<thead>.*?</thead>\s*<tbody>(.*?)</tbody>",
    re.IGNORECASE | re.DOTALL,
)

IO_TABLE_RE = re.compile(
    r"<h4>I/O Operations</h4>\s*<table.*?>\s*<thead>.*?</thead>\s*<tbody>(.*?)</tbody>",
    re.IGNORECASE | re.DOTALL,
)

TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(r"<code>(.*?)</code>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")

READ_RE = re.compile(r"^read\s*\([^)]*\)\s*(.*)$", re.IGNORECASE)


class SectionTableParser(HTMLParser):
    def __init__(self, target_h4: str) -> None:
        super().__init__()
        self.target_h4 = target_h4
        self.in_h4 = False
        self.h4_text = ""
        self.capture_next_table = False
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.in_th = False
        self.table = {"headers": [], "rows": []}
        self.current_row: List[str] = []
        self.cell_text = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "h4":
            self.in_h4 = True
            self.h4_text = ""
        elif tag == "table" and self.capture_next_table:
            self.in_table = True
            self.table = {"headers": [], "rows": []}
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag == "th" and self.in_tr:
            self.in_th = True
            self.cell_text = ""
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.cell_text = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4" and self.in_h4:
            title = " ".join(self.h4_text.split())
            if title == self.target_h4:
                self.capture_next_table = True
            self.in_h4 = False
            self.h4_text = ""
        elif tag == "th" and self.in_th:
            self.current_row.append(" ".join(self.cell_text.split()))
            self.in_th = False
            self.cell_text = ""
        elif tag == "td" and self.in_td:
            self.current_row.append(" ".join(self.cell_text.split()))
            self.in_td = False
            self.cell_text = ""
        elif tag == "tr" and self.in_tr:
            if self.current_row:
                if not self.table["headers"]:
                    self.table["headers"] = self.current_row
                else:
                    self.table["rows"].append(self.current_row)
            self.in_tr = False
            self.current_row = []
        elif tag == "table" and self.in_table:
            self.in_table = False
            self.capture_next_table = False

    def handle_data(self, data: str) -> None:
        if self.in_h4:
            self.h4_text += data
        if self.in_th or self.in_td:
            self.cell_text += data


@dataclass
class IoOp:
    line: str
    operation: str
    raw: str


@dataclass
class ProcUsage:
    name: str
    source_html: str
    filename_rows: List[Dict[str, str]]
    io_ops: List[IoOp]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def strip_tags(text: str) -> str:
    return TAG_RE.sub("", text).strip()


def parse_input_files_list(iofiles_html: str) -> Dict[str, str]:
    text = read_text(iofiles_html)
    match = INPUT_SECTION_RE.search(text)
    if not match:
        raise ValueError(f"Input files section not found in {iofiles_html}")
    section = match.group(0)
    files: Dict[str, str] = {}
    for href, name in INPUT_LINK_RE.findall(section):
        files[name.strip()] = href.strip()
    return files


def parse_filename_rows(html_text: str) -> List[Dict[str, str]]:
    match = FILENAME_TABLE_RE.search(html_text)
    if not match:
        return []
    rows_html = match.group(1)
    rows = re.findall(r"<tr>(.*?)</tr>", rows_html, re.IGNORECASE | re.DOTALL)
    result = []
    for row in rows:
        cells = [strip_tags(c) for c in TD_RE.findall(row)]
        if len(cells) < 5:
            continue
        result.append(
            {
                "type": cells[0],
                "component": cells[1],
                "default": cells[2],
                "hardcoded": cells[3],
                "file_cio": cells[4],
            }
        )
    return result


def parse_io_ops(html_text: str) -> List[IoOp]:
    match = IO_TABLE_RE.search(html_text)
    if not match:
        return []
    rows_html = match.group(1)
    rows = re.findall(r"<tr>(.*?)</tr>", rows_html, re.IGNORECASE | re.DOTALL)
    ops: List[IoOp] = []
    for row in rows:
        cells = TD_RE.findall(row)
        if len(cells) < 3:
            continue
        line = strip_tags(cells[0])
        operation = strip_tags(cells[1])
        raw_code = CODE_RE.search(cells[2])
        raw = strip_tags(raw_code.group(1)) if raw_code else strip_tags(cells[2])
        ops.append(IoOp(line=line, operation=operation, raw=raw))
    return ops


def parse_proc_usage(iofile_html: str) -> List[ProcUsage]:
    text = read_text(iofile_html)
    procs = []
    for proc_name, source_html in PROC_HEADER_RE.findall(text):
        filename_rows = parse_filename_rows(text)
        io_ops = parse_io_ops(text)
        procs.append(
            ProcUsage(
                name=proc_name.strip(),
                source_html=source_html.strip(),
                filename_rows=filename_rows,
                io_ops=io_ops,
            )
        )
    return procs


def read_statement_tail(raw: str) -> Optional[str]:
    match = READ_RE.match(raw.strip())
    if not match:
        return None
    return match.group(1).strip()


def extract_read_sequence(ops: List[IoOp]) -> List[str]:
    result = []
    for op in ops:
        if op.operation.lower() != "read":
            continue
        tail = read_statement_tail(op.raw)
        if tail:
            result.append(tail)
    return result


def parse_section_table(html_text: str, title: str) -> Dict[str, List[List[str]]]:
    parser = SectionTableParser(title)
    parser.feed(html_text)
    return parser.table


def rows_to_dicts(headers: List[str], rows: List[List[str]]) -> List[Dict[str, str]]:
    results = []
    for row in rows:
        entry = {}
        for idx, header in enumerate(headers):
            entry[header] = row[idx] if idx < len(row) else ""
        results.append(entry)
    return results


def compare_file_schema(old_table: Dict[str, List[List[str]]], new_table: Dict[str, List[List[str]]]) -> Dict[str, object]:
    old_headers = old_table.get("headers", [])
    new_headers = new_table.get("headers", [])
    old_rows = old_table.get("rows", [])
    new_rows = new_table.get("rows", [])

    old_dicts = rows_to_dicts(old_headers, old_rows)
    new_dicts = rows_to_dicts(new_headers, new_rows)

    def key(row: Dict[str, str]) -> Tuple[str, str, str]:
        line = row.get("Line in File", "")
        pos = row.get("Position in File", "")
        comp = row.get("Component", "")
        return (line, pos, comp)

    old_map = {key(r): r for r in old_dicts}
    new_map = {key(r): r for r in new_dicts}
    all_keys = sorted(set(old_map) | set(new_map))
    diffs = []
    for k in all_keys:
        old_row = old_map.get(k)
        new_row = new_map.get(k)
        if old_row != new_row:
            diffs.append({"key": k, "old": old_row, "new": new_row})

    ignored_cols = {"Default", "Units", "Description"}
    lite_diffs = []
    for k in all_keys:
        old_row = old_map.get(k) or {}
        new_row = new_map.get(k) or {}
        old_lite = {col: val for col, val in old_row.items() if col not in ignored_cols}
        new_lite = {col: val for col, val in new_row.items() if col not in ignored_cols}
        if old_lite != new_lite:
            lite_diffs.append({"key": k, "old": old_lite, "new": new_lite})

    return {
        "headers": old_headers or new_headers,
        "old": old_dicts,
        "new": new_dicts,
        "diff": diffs,
        "diff_lite": lite_diffs,
    }


def find_type_block(root: str, type_name: str) -> Optional[str]:
    type_re = re.compile(rf"^\s*type\s*(::)?\s*{re.escape(type_name)}\b", re.IGNORECASE)
    end_re = re.compile(r"^\s*end\s*type\b", re.IGNORECASE)
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if not filename.lower().endswith(".f90"):
                continue
            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    in_block = False
                    lines = []
                    for line in handle:
                        if not in_block and type_re.search(line):
                            in_block = True
                            lines.append(line)
                            continue
                        if in_block:
                            lines.append(line)
                            if end_re.search(line):
                                return "".join(lines)
            except OSError:
                continue
    return None


def extract_type_fields(type_block: str) -> List[str]:
    fields = []
    for line in type_block.splitlines():
        if "::" not in line:
            continue
        cleaned = line.split("!", 1)[0].strip()
        if not cleaned:
            continue
        if re.search(r"\bprocedure\b", cleaned, re.IGNORECASE):
            continue
        fields.append(cleaned)
    return fields


def extract_type_field_entries(type_block: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for line in type_block.splitlines():
        if "::" not in line:
            continue
        cleaned = line.split("!", 1)[0].strip()
        if not cleaned:
            continue
        if re.search(r"\bprocedure\b", cleaned, re.IGNORECASE):
            continue
        type_part, name_part = [part.strip() for part in cleaned.split("::", 1)]
        names = [n.strip().split("(")[0].strip() for n in name_part.split(",")]
        for name in names:
            if not name:
                continue
            entries.append({"name": name, "type": type_part})
    return entries


def collect_types_for_file(usages: List[ProcUsage]) -> List[str]:
    types = []
    for usage in usages:
        for row in usage.filename_rows:
            type_name = row.get("type", "").strip()
            if type_name and type_name not in types:
                types.append(type_name)
    return types


def compare_lists(old: List[str], new: List[str]) -> Dict[str, List[str]]:
    old_set = set(old)
    new_set = set(new)
    return {
        "added": sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "common": sorted(old_set & new_set),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare input files between two Ford outputs.")
    parser.add_argument("--old-docs", required=True, help="Path to older Ford docs output")
    parser.add_argument("--new-docs", required=True, help="Path to newer Ford docs output")
    parser.add_argument("--old-src", required=True, help="Path to older source tree")
    parser.add_argument("--new-src", required=True, help="Path to newer source tree")
    parser.add_argument("--out", required=True, help="Path to JSON report")
    parser.add_argument("--csv", help="Optional path to CSV summary output")
    parser.add_argument("--schema-csv", help="Optional path to per-row schema diff CSV")
    parser.add_argument("--schema-csv-lite", help="Optional path to schema diff CSV without defaults/units/description")
    parser.add_argument("--types-csv", help="Optional path to file/procedure/derived-type summary CSV")
    args = parser.parse_args()

    old_iofiles = os.path.join(args.old_docs, "lists", "iofiles.html")
    new_iofiles = os.path.join(args.new_docs, "lists", "iofiles.html")

    old_inputs = parse_input_files_list(old_iofiles)
    new_inputs = parse_input_files_list(new_iofiles)

    file_diff = compare_lists(list(old_inputs.keys()), list(new_inputs.keys()))

    report = {
        "summary": {
            "old_docs": args.old_docs,
            "new_docs": args.new_docs,
            "old_src": args.old_src,
            "new_src": args.new_src,
        },
        "input_files": {
            "added": file_diff["added"],
            "removed": file_diff["removed"],
            "common": [],
        },
        "files": {},
        "types": {},
    }

    for name in file_diff["common"]:
        old_page = os.path.join(args.old_docs, "iofile", "input", old_inputs[name])
        new_page = os.path.join(args.new_docs, "iofile", "input", new_inputs[name])
        old_html = read_text(old_page)
        new_html = read_text(new_page)
        old_usages = parse_proc_usage(old_page)
        new_usages = parse_proc_usage(new_page)

        old_procs = sorted({u.name for u in old_usages})
        new_procs = sorted({u.name for u in new_usages})
        proc_diff = compare_lists(old_procs, new_procs)

        old_reads = []
        new_reads = []
        for usage in old_usages:
            old_reads.extend(extract_read_sequence(usage.io_ops))
        for usage in new_usages:
            new_reads.extend(extract_read_sequence(usage.io_ops))

        file_schema = compare_file_schema(
            parse_section_table(old_html, "File Schema"),
            parse_section_table(new_html, "File Schema"),
        )

        file_schema_types = sorted(
            {
                row.get("TYPE", "").strip()
                for row in file_schema.get("old", []) + file_schema.get("new", [])
                if row.get("TYPE") and row.get("TYPE") != "-"
            }
        )

        report["files"][name] = {
            "procedures": proc_diff,
            "read_sequence": {
                "old": old_reads,
                "new": new_reads,
            },
            "filename_rows": {
                "old": [row for usage in old_usages for row in usage.filename_rows],
                "new": [row for usage in new_usages for row in usage.filename_rows],
            },
            "file_schema": file_schema,
            "file_schema_types": file_schema_types,
            "procedures_list": sorted({u.name for u in old_usages + new_usages}),
        }

        report["input_files"]["common"].append(name)

    all_type_names = set()
    for name in report["files"].keys():
        old_rows = report["files"][name]["filename_rows"]["old"]
        new_rows = report["files"][name]["filename_rows"]["new"]
        for row in old_rows + new_rows:
            if row.get("type"):
                all_type_names.add(row["type"].strip())

    for type_name in sorted(all_type_names):
        old_block = find_type_block(args.old_src, type_name)
        new_block = find_type_block(args.new_src, type_name)
        old_fields = extract_type_fields(old_block) if old_block else []
        new_fields = extract_type_fields(new_block) if new_block else []
        old_entries = extract_type_field_entries(old_block) if old_block else []
        new_entries = extract_type_field_entries(new_block) if new_block else []
        report["types"][type_name] = {
            "old_fields": old_fields,
            "new_fields": new_fields,
            "old_entries": old_entries,
            "new_entries": new_entries,
        }

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "input_file",
                    "status",
                    "procedures_added",
                    "procedures_removed",
                    "read_sequence_changed",
                    "file_schema_changed",
                ]
            )
            added_set = set(report["input_files"]["added"])
            removed_set = set(report["input_files"]["removed"])
            for name in sorted(report["files"].keys()):
                status = "common"
                if name in added_set:
                    status = "added"
                elif name in removed_set:
                    status = "removed"
                proc_diff = report["files"][name]["procedures"]
                old_reads = report["files"][name]["read_sequence"]["old"]
                new_reads = report["files"][name]["read_sequence"]["new"]
                schema_diff = report["files"][name]["file_schema"]["diff"]
                writer.writerow(
                    [
                        name,
                        status,
                        ";".join(proc_diff.get("added", [])),
                        ";".join(proc_diff.get("removed", [])),
                        "Y" if old_reads != new_reads else "N",
                        "Y" if schema_diff else "N",
                    ]
                )

    if args.schema_csv:
        with open(args.schema_csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "input_file",
                    "line_in_file",
                    "position_in_file",
                    "component",
                    "old_row",
                    "new_row",
                ]
            )
            for name in sorted(report["files"].keys()):
                diffs = report["files"][name]["file_schema"]["diff"]
                for diff in diffs:
                    line, pos, comp = diff["key"]
                    writer.writerow(
                        [
                            name,
                            line,
                            pos,
                            comp,
                            diff.get("old"),
                            diff.get("new"),
                        ]
                    )

    if args.schema_csv_lite:
        with open(args.schema_csv_lite, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "input_file",
                    "line_in_file",
                    "position_in_file",
                    "component",
                    "old_row",
                    "new_row",
                ]
            )
            for name in sorted(report["files"].keys()):
                diffs = report["files"][name]["file_schema"]["diff_lite"]
                for diff in diffs:
                    line, pos, comp = diff["key"]
                    writer.writerow(
                        [
                            name,
                            line,
                            pos,
                            comp,
                            diff.get("old"),
                            diff.get("new"),
                        ]
                    )

    if args.types_csv:
        with open(args.types_csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "input_file",
                    "procedures",
                    "derived_types",
                    "derived_type_changes",
                ]
            )
            for name in sorted(report["files"].keys()):
                file_entry = report["files"][name]
                types_used = file_entry.get("file_schema_types", [])
                changed_types = []
                for type_name in types_used:
                    type_info = report["types"].get(type_name, {})
                    if type_info.get("old_entries") != type_info.get("new_entries"):
                        changed_types.append(type_name)
                writer.writerow(
                    [
                        name,
                        ";".join(file_entry.get("procedures_list", [])),
                        ";".join(types_used),
                        ";".join(changed_types),
                    ]
                )

    print("Input files added:", len(report["input_files"]["added"]))
    print("Input files removed:", len(report["input_files"]["removed"]))
    print("Common input files:", len(report["input_files"]["common"]))
    print("Wrote report:", args.out)
    if args.csv:
        print("Wrote CSV summary:", args.csv)
    if args.schema_csv:
        print("Wrote schema diff CSV:", args.schema_csv)
    if args.schema_csv_lite:
        print("Wrote schema diff CSV (lite):", args.schema_csv_lite)
    if args.types_csv:
        print("Wrote types CSV:", args.types_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
