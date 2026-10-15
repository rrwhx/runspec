#!/usr/bin/env python3
"""Add reproducible uniform noise to selected numeric CSV columns."""

import argparse

import numpy as np
import pandas as pd

from _csv_common import (
    add_csv_options,
    column_list,
    parse_args,
    read_frame,
    require_columns,
    run_cli,
    write_frame,
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Add uniform random noise to selected numeric columns.",
        epilog="Example: csv_add_random.py data.csv -c value -r -0.5 0.5 --seed 42",
    )
    parser.add_argument("file", nargs="?", help="Input file; omitted or '-' reads stdin")
    parser.add_argument("-i", "--input", help="Input file (alias for the positional argument)")
    add_csv_options(parser)
    parser.add_argument("-c", "--columns", required=True, help="Comma-separated numeric columns")
    parser.add_argument(
        "-r",
        "--range",
        type=float,
        nargs=2,
        required=True,
        metavar=("MIN", "MAX"),
        help="Uniform noise range",
    )
    parser.add_argument("--seed", type=int, help="Non-negative random seed")
    args = parse_args(parser, argv)
    if args.file is not None and args.input is not None:
        parser.error("Specify either FILE or --input, not both")
    low, high = args.range
    if not np.isfinite([low, high]).all() or low > high:
        parser.error("Range must be finite with MIN <= MAX")
    if args.seed is not None and args.seed < 0:
        parser.error("--seed must be non-negative")
    columns = column_list(args.columns)
    # Preserve all untouched fields, including leading zeroes and literal NA strings.
    frame = read_frame(args.input or args.file, args, strings=True)
    require_columns(frame, columns)
    rng = np.random.default_rng(args.seed)
    for column in columns:
        numeric = pd.to_numeric(frame[column].replace("", np.nan), errors="raise")
        frame[column] = numeric + rng.uniform(low, high, len(frame))
    write_frame(frame, args)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
