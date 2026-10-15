#!/usr/bin/env python3
"""Split a CSV into files by one or more explicitly selected columns."""

import argparse
import csv
import os
import re
import tempfile
from collections import OrderedDict
from itertools import chain
from pathlib import Path

from _csv_common import (
    add_csv_options,
    csv_writer,
    open_input,
    parse_args,
    resolve_columns,
    run_cli,
    same_file,
)


def safe_filename(value, maxbytes=150):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f\s]', "_", value).strip("._-") or "EMPTY"
    # Limit bytes, not characters, so Unicode group names fit filesystem limits.
    return value.encode("utf-8")[:maxbytes].decode("utf-8", errors="ignore") or "EMPTY"


def split_rows(reader, first, indices, args, staging, directory, prefix):
    header = None if args.no_header_row else first
    handles = OrderedDict()
    filenames, used_names = {}, set()
    try:
        for row in chain([first] if args.no_header_row else [], reader):
            if any(index >= len(row) for index in indices):
                if args.missing == "error":
                    raise ValueError(f"Missing split column near input line {reader.line_num}")
                if args.missing == "skip":
                    continue
                key = None
            else:
                key = tuple(row[index] for index in indices)
            is_new = key not in filenames
            if is_new:
                stem = prefix + safe_filename("_".join(key) if key is not None else "MISSING")
                name, suffix = stem + ".csv", 2
                while name.casefold() in used_names:
                    name = f"{stem}_{suffix}.csv"
                    suffix += 1
                if same_file(args.input, directory / name):
                    raise ValueError(f"Output would overwrite input: {directory / name}")
                filenames[key] = name
                used_names.add(name.casefold())
            name = filenames[key]
            if name in handles:
                stream, writer = handles.pop(name)
            else:
                if len(handles) >= args.max_open_files:
                    _, (old_stream, _) = handles.popitem(last=False)
                    old_stream.close()
                stream = open(
                    staging / name,
                    "w" if is_new else "a",
                    encoding=args.output_encoding,
                    newline="",
                )
                writer = csv_writer(stream, args)
                handles[name] = stream, writer
                if is_new and header is not None:
                    writer.writerow(header)
            handles[name] = stream, writer
            writer.writerow(row)
    finally:
        for stream, _ in handles.values():
            stream.close()
    return filenames.values()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: csv_split_by_column.py sales.csv -c region,category -o parts",
    )
    parser.add_argument("input", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser, output=False)
    parser.add_argument(
        "-c", "--columns", required=True, help="Comma-separated names or zero-based indices"
    )
    parser.add_argument(
        "-o", "--output", default="out_split", help="Output directory (default: out_split)"
    )
    parser.add_argument(
        "--prefix", help="Filename prefix; default: input stem followed by an underscore"
    )
    parser.add_argument(
        "-H", "--no-header-row", action="store_true", help="Input contains data rows only"
    )
    parser.add_argument(
        "--missing",
        choices=("error", "skip", "group"),
        default="error",
        help="Handle rows missing a split column (default: error)",
    )
    parser.add_argument("--keep-missing", action="store_true", help="Alias for --missing group")
    parser.add_argument(
        "--max-open-files",
        type=int,
        default=64,
        help="Maximum concurrently open output files (default: 64)",
    )
    args = parse_args(parser, argv)
    if args.max_open_files < 1:
        parser.error("--max-open-files must be positive")
    if args.keep_missing:
        if args.missing not in ("error", "group"):
            parser.error("--keep-missing conflicts with --missing skip")
        args.missing = "group"
    stem = Path(args.input).stem if args.input and args.input != "-" else "stdin"
    prefix = args.prefix if args.prefix is not None else safe_filename(stem, 60) + "_"
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', prefix) or len(prefix.encode("utf-8")) > 64:
        parser.error(
            "--prefix must be a filename prefix of at most 64 UTF-8 bytes, without path separators"
        )
    directory = Path(args.output)
    with open_input(args.input, args.encoding) as source:
        reader = csv.reader(source, delimiter=args.delimiter, strict=True)
        first = next(reader, None)
        if first is None:
            return
        indices = resolve_columns(args.columns, None if args.no_header_row else first, len(first))
        directory.mkdir(parents=True, exist_ok=True)
        # Stage output so malformed input does not truncate existing partitions.
        with tempfile.TemporaryDirectory(dir=directory, prefix=".csv-split-") as temporary:
            staging = Path(temporary)
            filenames = split_rows(reader, first, indices, args, staging, directory, prefix)
            for name in filenames:
                os.replace(staging / name, directory / name)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
