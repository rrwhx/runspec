#!/usr/bin/env python3
"""Combine selected columns from multiple CSV files by row position."""

import argparse
from pathlib import Path

from _csv_common import add_csv_options, csv_writer, open_output, parse_args, read_rows, run_cli


def parse_items(tokens):
    """Parse runs of FILE [FILE ...] INDEX [INDEX ...]."""
    groups, files, columns = [], [], []
    for token in tokens:
        try:
            column = int(token)
        except ValueError:
            if columns:
                groups.append((files, columns))
                files, columns = [], []
            files.append(token)
        else:
            if not files:
                raise ValueError(f"Column index {token} must follow an input file")
            columns.append(column)
    if files:
        if not columns:
            raise ValueError(f"Missing column indices after: {', '.join(files)}")
        groups.append((files, columns))
    if not groups:
        raise ValueError("At least one file and column index are required")
    return groups


def read_csv_columns(
    filename,
    col_indices,
    *,
    delimiter=",",
    encoding="utf-8-sig",
    skip_header=False,
    missing="empty",
):
    rows = read_rows(filename, delimiter=delimiter, encoding=encoding)
    if skip_header:
        rows = rows[1:]
    extracted = []
    for line, row in enumerate(rows, 2 if skip_header else 1):
        selected = []
        for index in col_indices:
            if -len(row) <= index < len(row):
                selected.append(row[index])
            elif missing == "empty":
                selected.append("")
            else:
                raise ValueError(f"Column {index} missing in {filename}, record {line}")
        extracted.append(selected)
    return extracted


def generate_header(groups):
    return [
        f"{Path(filename).stem if filename != '-' else 'stdin'}_col{index}"
        for files, columns in groups
        for filename in files
        for index in columns
    ]


def combine(groups, **options):
    """Return a generated header and rows, padding every requested column."""
    if sum(filename == "-" for files, _ in groups for filename in files) > 1:
        raise ValueError("stdin may only be specified once")
    blocks = [
        (read_csv_columns(filename, columns, **options), len(columns))
        for files, columns in groups
        for filename in files
    ]
    rows = []
    for index in range(max((len(data) for data, _ in blocks), default=0)):
        rows.append(
            [
                cell
                for data, width in blocks
                for cell in (data[index] if index < len(data) else [""] * width)
            ]
        )
    return generate_header(groups), rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: csv_combine.py a.csv b.csv 1 2 c.csv -1; integer filenames need ./ prefix.",
    )
    add_csv_options(parser)
    parser.add_argument(
        "items",
        nargs="+",
        metavar="FILE|INDEX",
        help="FILE [FILE ...] INDEX [INDEX ...], repeatable groups",
    )
    parser.add_argument("--no-header", action="store_true", help="Omit the generated output header")
    parser.add_argument(
        "--skip-header", action="store_true", help="Skip the first row of each input"
    )
    parser.add_argument(
        "--missing",
        choices=("empty", "error"),
        default="empty",
        help="Handle missing selected cells (default: empty)",
    )
    args = parse_args(parser, argv)
    groups = parse_items(args.items)
    header, rows = combine(
        groups,
        delimiter=args.delimiter,
        encoding=args.encoding,
        skip_header=args.skip_header,
        missing=args.missing,
    )
    with open_output(args.output, args.output_encoding) as output:
        writer = csv_writer(output, args)
        if not args.no_header:
            writer.writerow(header)
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
