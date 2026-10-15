#!/usr/bin/env python3
"""Sample and concatenate CSV rows without converting their field values."""

import argparse
import csv
import random
from itertools import chain
from pathlib import Path

from _csv_common import (
    add_csv_options,
    csv_writer,
    open_input,
    open_output,
    parse_args,
    run_cli,
    same_file,
)


def collect_files(inputs, output, pattern):
    files = []
    identities = set()
    for source in inputs or ["-"]:
        if source == "-":
            candidates = ["-"]
        elif Path(source).is_dir():
            candidates = [
                str(path) for path in sorted(Path(source).glob(pattern)) if path.is_file()
            ]
        elif Path(source).is_file():
            candidates = [source]
        else:
            raise ValueError(f"Input path does not exist: {source}")
        for path in candidates:
            if same_file(path, output):
                continue
            if path == "-":
                identity = ("stdin",)
            else:
                info = Path(path).stat()
                identity = (info.st_dev, info.st_ino)
            if identity not in identities:
                identities.add(identity)
                files.append(path)
    if not files:
        raise ValueError("No input files found after excluding the output file")
    return files


def checked_rows(reader, width):
    for index, row in enumerate(reader, 1):
        if width is None:
            width = len(row)
        if len(row) != width:
            raise ValueError(f"Inconsistent row width near data record {index}")
        yield row


def reservoir_sample(records, count, rng):
    """Select at most count rows in one pass, using O(count) memory."""
    sample = []
    for index, row in enumerate(records):
        if index < count:
            sample.append((index, row))
        elif count:
            slot = rng.randrange(index + 1)
            if slot < count:
                sample[slot] = (index, row)
    return [row for _, row in sorted(sample)]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sample each input file and concatenate the selected rows.",
        epilog="Example: csv_sample.py data/ -r 0.1 --seed 42 -o sample.csv",
    )
    parser.add_argument(
        "inputs", nargs="*", help="Files or directories; omitted or '-' reads stdin"
    )
    add_csv_options(parser)
    parser.add_argument(
        "-r",
        "--sample-rate",
        type=float,
        default=1.0,
        help="Fraction per file, from 0 to 1 (default: 1)",
    )
    parser.add_argument(
        "-n", "--sample-rows", type=int, help="Maximum rows per file; takes precedence over -r"
    )
    parser.add_argument("-m", "--method", choices=("random", "uniform"), default="random")
    parser.add_argument("--seed", type=int, help="Non-negative random seed")
    parser.add_argument(
        "--pattern", default="*.csv", help="Directory glob pattern (default: *.csv)"
    )
    parser.add_argument(
        "-H", "--no-header-row", action="store_true", help="Input contains data rows only"
    )
    args = parse_args(parser, argv)
    if args.sample_rows is not None:
        if args.sample_rows < 0:
            parser.error("--sample-rows must be non-negative")
    elif not 0 <= args.sample_rate <= 1:
        parser.error("--sample-rate must be between 0 and 1")
    if args.seed is not None and args.seed < 0:
        parser.error("--seed must be non-negative")
    files = collect_files(args.inputs, args.output, args.pattern)
    rng = random.Random(args.seed)
    expected_header, width = None, None
    with open_output(args.output, args.output_encoding) as output:
        writer = csv_writer(output, args)
        for path in files:
            with open_input(path, args.encoding) as stream:
                reader = csv.reader(stream, delimiter=args.delimiter, strict=True)
                if not args.no_header_row:
                    header = next(reader, None)
                    if header is None:
                        raise ValueError(f"Input has no header: {path}")
                    if expected_header is None:
                        expected_header, width = header, len(header)
                        writer.writerow(header)
                    elif header != expected_header:
                        raise ValueError(f"Input columns do not match: {path}")
                records = reader
                if args.no_header_row and width is None:
                    first = next(reader, None)
                    if first is not None:
                        width = len(first)
                        records = chain([first], reader)
                records = checked_rows(records, width)
                if args.sample_rows == 0 or (args.sample_rows is None and args.sample_rate == 0):
                    for _ in records:
                        pass
                    continue
                if args.sample_rows is None and args.sample_rate == 1:
                    writer.writerows(records)
                    continue
                if args.sample_rows is not None and args.method == "random":
                    writer.writerows(reservoir_sample(records, args.sample_rows, rng))
                    continue
                records = list(records)
            count = len(records)
            size = (
                min(args.sample_rows, count)
                if args.sample_rows is not None
                else int(count * args.sample_rate)
            )
            if args.method == "random":
                indices = sorted(rng.sample(range(count), size)) if size < count else range(count)
            else:
                indices = [index * count // size for index in range(size)]
            writer.writerows(records[index] for index in indices)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
