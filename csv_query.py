#!/usr/bin/env python3
"""Filter, aggregate and sort CSV data by explicitly selected columns."""

import argparse

import pandas as pd

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


def parse_agg_args(items):
    spec = {}
    for item in items:
        parts = [part.strip() for part in item.split(":")]
        column, functions = parts[0], parts[1:] or ["mean"]
        if not column or any(function not in AGGREGATIONS for function in functions):
            raise ValueError(f"Invalid aggregation: {item!r}; supported: {', '.join(AGGREGATIONS)}")
        spec.setdefault(column, [])
        spec[column].extend(function for function in functions if function not in spec[column])
    return {
        column: functions[0] if len(functions) == 1 else functions
        for column, functions in spec.items()
    }


def aggregate(frame, groups, spec, dropna=False):
    require_columns(frame, groups + list(spec))
    if not spec:
        name = "count" if "count" not in groups else "row_count"
        while name in groups:
            name = "_" + name
        return frame.groupby(groups, dropna=dropna, sort=False).size().reset_index(name=name)
    if groups:
        result = frame.groupby(groups, dropna=dropna, sort=False).agg(spec)
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = ["_".join(map(str, column)) for column in result.columns]
        else:
            result.columns = [
                f"{column}_{spec[column]}" if column in groups else column
                for column in result.columns
            ]
        if any(column in groups for column in result.columns) or result.columns.has_duplicates:
            raise ValueError(
                "Aggregation produces duplicate column names; change the grouping or aggregations"
            )
        return result.reset_index()
    # Explicit per-column reduction also returns one row for an empty input.
    multiple = any(isinstance(functions, list) for functions in spec.values())
    values = {}
    for column, functions in spec.items():
        for function in functions if isinstance(functions, list) else [functions]:
            name = f"{column}_{function}" if multiple else column
            if name in values:
                raise ValueError(f"Aggregation produces duplicate column name: {name}")
            series = frame[column]
            if function == "size":
                value = len(series)
            elif function in ("first", "last"):
                nonempty = series.dropna()
                value = nonempty.iloc[0 if function == "first" else -1] if len(nonempty) else None
            else:
                value = series.agg(function)
            values[name] = value
    return pd.DataFrame([values])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Filter, group, aggregate and sort a CSV.",
        epilog="Example: csv_query.py sales.csv -f 'quantity > 0' -g category -a amount:sum -s amount:desc",
    )
    parser.add_argument("file", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser, dataframe=True)
    parser.add_argument(
        "-f", "--filter", action="append", default=[], help="Pandas query expression; repeatable"
    )
    parser.add_argument("-g", "--groupby", help="Comma-separated grouping columns")
    parser.add_argument(
        "-a",
        "--agg",
        action="append",
        default=[],
        help="COLUMN:FUNC[:FUNC], comma-separated or repeated; default FUNC=mean",
    )
    parser.add_argument("-s", "--sort", help="COLUMN[:asc|desc], comma-separated")
    parser.add_argument("--limit", type=int, help="Maximum output rows (0 outputs only the header)")
    parser.add_argument(
        "--drop-na-groups",
        action="store_true",
        help="Drop rows with missing group keys (default: keep)",
    )
    args = parse_args(parser, argv)
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be non-negative")
    groups = column_list(args.groupby) if args.groupby is not None else []
    spec = parse_agg_args([item for arg in args.agg for item in arg.split(",")])
    frame = read_frame(args.file, args)
    for expression in args.filter:
        frame = frame.query(expression, engine="python")
    if groups or spec:
        frame = aggregate(frame, groups, spec, args.drop_na_groups)
    if args.sort is not None:
        columns, ascending = [], []
        for item in column_list(args.sort):
            column, separator, order = item.partition(":")
            column, order = column.strip(), order.strip().lower()
            if not column or (separator and order not in ("asc", "desc")):
                raise ValueError(f"Invalid sort specification: {item}")
            columns.append(column)
            ascending.append(order != "desc")
        require_columns(frame, columns)
        frame = frame.sort_values(columns, ascending=ascending, kind="stable")
    if args.limit is not None:
        frame = frame.head(args.limit)
    write_frame(frame, args)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
