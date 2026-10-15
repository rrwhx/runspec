#!/usr/bin/env python3
"""Merge CSV tables horizontally or vertically, with optional key-based deduplication."""

import argparse
import csv

from _csv_common import add_csv_options, csv_writer, open_output, parse_args, read_rows, run_cli

# Retain the public read helper for callers importing this module.
read_csv = read_rows


def _row_width(rows):
    return max((len(row) for row in rows), default=0)


def _pad(row, width):
    return list(row) + [""] * (width - len(row))


def _dedup_columns(rows):
    if not rows:
        return rows
    seen, keep = set(), []
    for index, key in enumerate(rows[0]):
        if not key or key not in seen:
            keep.append(index)
            seen.add(key)
    return [[row[index] for index in keep] for row in rows]


def _dedup_rows(rows):
    seen, result = set(), []
    for row in rows:
        key = row[0] if row else ""
        if not key or key not in seen:
            result.append(row)
            seen.add(key)
    return result


def _read_blocks(files, delimiter, encoding):
    files = list(files)
    if files.count("-") > 1:
        raise ValueError("stdin may only be specified once")
    return [read_rows(path, delimiter=delimiter, encoding=encoding) for path in files]


def merge_horizontal(
    files, keep_all=False, dedup=False, *, delimiter=",", encoding="utf-8-sig", by_position=False
):
    """Share the leading key column unless keep_all; pad unequal lengths."""
    blocks = _read_blocks(files, delimiter, encoding)
    widths = [_row_width(block) for block in blocks]
    merged = []
    for index in range(max((len(block) for block in blocks), default=0)):
        parts = [
            _pad(block[index] if index < len(block) else [], width)
            for block, width in zip(blocks, widths)
        ]
        if keep_all:
            row = [cell for part in parts for cell in part]
        else:
            keys = [part[0] for part in parts if part and part[0]]
            if not by_position and len(set(keys)) > 1:
                raise ValueError(
                    f"Leading keys do not match at record {index + 1}: {keys}; use --by-position or --keep-all if intended"
                )
            row = [keys[0] if keys else ""] if any(widths) else []
            row.extend(cell for part in parts for cell in part[1:])
        merged.append(row)
    return _dedup_columns(merged) if dedup else merged


def merge_vertical(
    files, keep_all=False, dedup=False, *, delimiter=",", encoding="utf-8-sig", by_position=False
):
    """Share the first non-empty header unless keep_all; pad unequal widths."""
    blocks = _read_blocks(files, delimiter, encoding)
    rows, header = [], None
    for block in blocks:
        if not block:
            continue
        if keep_all:
            rows.extend(block)
        elif header is None:
            header = block[0]
            rows.extend(block)
        else:
            if not by_position and block[0] != header:
                raise ValueError(
                    "Input headers do not match; use --by-position or --keep-all if intended"
                )
            rows.extend(block[1:])
    width = _row_width(rows)
    rows = [_pad(row, width) for row in rows]
    if dedup:
        rows = [rows[0]] + _dedup_rows(rows[1:]) if rows and not keep_all else _dedup_rows(rows)
    return rows


def merge_csv(files, axis="h", keep_all=False, dedup=False, **options):
    if axis in ("h", "horizontal"):
        return merge_horizontal(files, keep_all, dedup, **options)
    if axis in ("v", "vertical"):
        return merge_vertical(files, keep_all, dedup, **options)
    raise ValueError(f"Unknown merge axis: {axis}; expected h or v")


def write_csv(rows, output=None, *, delimiter=",", encoding="utf-8"):
    with open_output(output, encoding) as stream:
        csv.writer(stream, delimiter=delimiter, lineterminator="\n").writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: csv_merge.py -v part1.csv part2.csv -o merged.csv",
    )
    add_csv_options(parser)
    parser.add_argument("files", nargs="*", help="Input files; omitted or '-' reads stdin")
    parser.add_argument(
        "-v",
        "--vertical",
        action="store_true",
        help="Stack files vertically (default: side by side)",
    )
    parser.add_argument(
        "-k",
        "--keep-all",
        action="store_true",
        help="Keep all leading columns/rows, including repeated keys/headers",
    )
    parser.add_argument(
        "-u",
        "--dedup",
        action="store_true",
        help="Keep first occurrence by column header (horizontal) or leading cell (vertical)",
    )
    parser.add_argument(
        "--by-position",
        action="store_true",
        help="Allow different leading keys/headers and merge by position",
    )
    args = parse_args(parser, argv)
    rows = merge_csv(
        args.files or ["-"],
        "v" if args.vertical else "h",
        args.keep_all,
        args.dedup,
        delimiter=args.delimiter,
        encoding=args.encoding,
        by_position=args.by_position,
    )
    with open_output(args.output, args.output_encoding) as output:
        csv_writer(output, args).writerows(rows)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
