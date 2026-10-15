#!/usr/bin/env python3
"""Convert a long CSV to a wide table using caller-selected columns."""

import argparse

from _csv_common import (
    AGGREGATIONS,
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
        description="Pivot a CSV from long to wide form.",
        epilog="Example: csv_pivot.py sales.csv -i product -c region -v amount -a sum",
    )
    parser.add_argument("file", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser, dataframe=True)
    parser.add_argument("-i", "--index", required=True, help="Comma-separated row key columns")
    parser.add_argument(
        "-c", "--columns", required=True, help="Column whose values become output column names"
    )
    parser.add_argument("-v", "--values", required=True, help="Column containing cell values")
    parser.add_argument(
        "-a",
        "--aggfunc",
        choices=AGGREGATIONS,
        help="Aggregate duplicate keys; omitted means duplicates are errors",
    )
    parser.add_argument(
        "--drop-na", action="store_true", help="Drop output rows containing missing values"
    )
    parser.add_argument(
        "--fill-value", type=float, help="Explicitly fill missing result cells with this number"
    )
    args = parse_args(parser, argv)
    index = column_list(args.index)
    column, value = args.columns.strip(), args.values.strip()
    if column in index or value in index or column == value:
        parser.error("Index, column and value selectors must be distinct")
    frame = read_frame(args.file, args)
    require_columns(frame, index + [column, value])
    keys = index + [column]
    if args.aggfunc:
        # Aggregate only observed combinations, keeping missing group keys.
        grouped = frame.groupby(keys, sort=False, dropna=False, observed=True)[value]
        frame = grouped.agg(args.aggfunc).reset_index(name=value)
    elif frame.duplicated(keys).any():
        raise ValueError("Duplicate pivot keys; specify -a/--aggfunc to aggregate them")
    wide = frame.pivot(index=index, columns=column, values=value)
    wide.columns = [str(name) for name in wide.columns]
    if wide.columns.has_duplicates or any(name in index for name in wide.columns):
        raise ValueError("Pivot values produce duplicate output column names")
    wide = wide.reset_index()
    if args.fill_value is not None:
        data_columns = [name for name in wide.columns if name not in index]
        wide[data_columns] = wide[data_columns].fillna(args.fill_value)
    if args.drop_na:
        wide = wide.dropna()
    write_frame(wide, args)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
