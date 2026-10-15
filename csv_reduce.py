#!/usr/bin/env python3
"""Reduce numeric columns per key, optionally adding SPEC group summaries."""

import argparse
import csv
import math
import re
import statistics

from _csv_common import (
    add_csv_options,
    csv_writer,
    open_input,
    open_output,
    parse_args,
    resolve_columns,
    run_cli,
)

METHODS = (
    "sum",
    "mean",
    "arithmetic",
    "geometric",
    "harmonic",
    "hmean",
    "median",
    "product",
    "max",
    "min",
)


def reduce_values(method, values):
    if not values:
        raise ValueError("Cannot reduce an empty set of values")
    if method == "geometric":
        if any(value < 0 for value in values):
            raise ValueError("Geometric mean requires non-negative values")
        result = 0.0 if 0 in values else math.exp(statistics.fmean(map(math.log, values)))
    elif method in ("harmonic", "hmean"):
        if any(value < 0 for value in values):
            raise ValueError("Harmonic mean requires non-negative values")
        result = statistics.harmonic_mean(values)
    elif method in ("mean", "arithmetic"):
        result = statistics.fmean(values)
    elif method == "sum":
        result = math.fsum(values)
    elif method == "product":
        result = math.prod(values)
    elif method == "median":
        result = statistics.median(values)
    elif method == "max":
        result = max(values)
    elif method == "min":
        result = min(values)
    else:
        raise ValueError(f"Unsupported reduction method: {method}")
    if not math.isfinite(result):
        raise ValueError(f"{method} produced a non-finite value")
    return result


def group_name(key):
    if key.startswith(("int_", "xfp_")):
        return key[:3]
    return key.split("-", 1)[0] if "-" in key else "all"


def reduce_rows(reader, key_index, value_indices, width, args):
    buckets = {}
    for row in reader:
        if len(row) != width:
            raise ValueError(f"Inconsistent row width near input line {reader.line_num}")
        key = row[key_index]
        if not key:
            raise ValueError(f"Empty key near input line {reader.line_num}")
        if args.key_mode == "spec":
            key = re.sub(r"_\d+$", "", key)
        try:
            values = [float(row[index]) for index in value_indices]
        except ValueError as exc:
            raise ValueError(f"Non-numeric value near input line {reader.line_num}") from exc
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"Non-finite value near input line {reader.line_num}")
        buckets.setdefault(key, []).append(values)
    reduced = {
        key: [reduce_values(args.reduce, values) for values in zip(*records)]
        for key, records in buckets.items()
    }
    if args.no_group_summary or args.reduce2 in ("", "none"):
        return [[key, *values] for key, values in reduced.items()]
    groups = {}
    for key, values in reduced.items():
        groups.setdefault(group_name(key), []).append((key, values))
    rows = []
    for group, items in groups.items():
        # Keep qualified keys: int_example and xfp_example must remain distinct.
        rows.extend([key, *values] for key, values in items)
        summary_name = f"{group}_{args.reduce2}"
        if summary_name in reduced:
            raise ValueError(
                f"Summary key conflicts with a data key: {summary_name}; use --no-group-summary"
            )
        values = [
            reduce_values(args.reduce2, column) for column in zip(*(values for _, values in items))
        ]
        rows.append([summary_name, *values])
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: csv_reduce.py data.csv --key category --key-mode exact -e amount -r geometric --no-group-summary",
    )
    parser.add_argument("input", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser)
    parser.add_argument(
        "--key", default="0", help="Key column name or zero-based index (default: 0)"
    )
    parser.add_argument(
        "--key-mode",
        choices=("spec", "exact"),
        default="spec",
        help="Strip trailing _NUMBER for SPEC runs, or keep exact keys (default: spec)",
    )
    parser.add_argument(
        "-e",
        "--event",
        help="Numeric columns by name/index/range, comma-separated (default: all except key)",
    )
    parser.add_argument(
        "-r",
        "--reduce",
        type=str.lower,
        choices=METHODS,
        default="sum",
        help="Reduction per key (default: sum)",
    )
    parser.add_argument(
        "-r2",
        "--reduce2",
        type=str.lower,
        choices=METHODS + ("none", ""),
        default="mean",
        help="Reduction per SPEC group (default: mean); none disables summaries",
    )
    parser.add_argument("--no-group-summary", action="store_true", help="Output per-key rows only")
    args = parse_args(parser, argv)
    with open_input(args.input, args.encoding) as source:
        reader = csv.reader(source, delimiter=args.delimiter, strict=True)
        header = next(reader, None)
        if not header:
            raise ValueError("Input must contain a header")
        key_indices = resolve_columns(args.key, header, len(header))
        if len(key_indices) != 1:
            parser.error("--key must select exactly one column")
        key_index = key_indices[0]
        value_indices = (
            resolve_columns(args.event, header, len(header), ranges=True)
            if args.event is not None
            else [index for index in range(len(header)) if index != key_index]
        )
        if not value_indices or key_index in value_indices:
            parser.error("Select at least one numeric column, excluding the key column")
        result = reduce_rows(reader, key_index, value_indices, len(header), args)
    with open_output(args.output, args.output_encoding) as output:
        writer = csv_writer(output, args)
        writer.writerow([header[key_index], *[header[index] for index in value_indices]])
        writer.writerows(result)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
