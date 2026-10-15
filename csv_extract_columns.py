#!/usr/bin/env python3
"""Select or exclude CSV columns by name, zero-based index, or index range."""

import argparse
import csv
from itertools import chain

from _csv_common import (
    add_csv_options,
    csv_writer,
    open_input,
    open_output,
    parse_args,
    resolve_columns,
    run_cli,
    same_file,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser)
    parser.add_argument(
        "-c", "--columns", help="Comma-separated selectors, e.g. name,0,2-4; default: all"
    )
    parser.add_argument("-C", "--not-columns", help="Selectors to exclude after applying -c")
    parser.add_argument(
        "-H", "--no-header-row", action="store_true", help="Input contains data rows only"
    )
    parser.add_argument(
        "--missing",
        choices=("error", "empty"),
        default="error",
        help="Handle rows shorter than the header (default: error)",
    )
    args = parse_args(parser, argv)
    if same_file(args.file, args.output):
        parser.error("Input and output must be different files")
    with open_input(args.file, args.encoding) as source:
        reader = csv.reader(source, delimiter=args.delimiter, strict=True)
        first = next(reader, None)
        if first is None:
            with open_output(args.output, args.output_encoding):
                pass
            return
        header = None if args.no_header_row else first
        indices = (
            resolve_columns(args.columns, header, len(first), ranges=True)
            if args.columns is not None
            else list(range(len(first)))
        )
        if args.not_columns is not None:
            excluded = resolve_columns(args.not_columns, header, len(first), ranges=True)
            indices = [index for index in indices if index not in excluded]
        with open_output(args.output, args.output_encoding) as output:
            writer = csv_writer(output, args)
            for row in chain([first], reader):
                if len(row) > len(first):
                    raise ValueError(f"Row longer than expected near input line {reader.line_num}")
                if len(row) < len(first) and args.missing == "error":
                    raise ValueError(f"Row shorter than expected near input line {reader.line_num}")
                writer.writerow([row[index] if index < len(row) else "" for index in indices])


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
