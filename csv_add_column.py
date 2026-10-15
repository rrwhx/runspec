#!/usr/bin/env python3
"""Append a computed column using zero-based column references."""

import argparse
import ast
import csv
import sys
from itertools import chain

from _csv_common import add_csv_options, csv_writer, open_input, open_output, parse_args, run_cli

FUNCTIONS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "int": int,
    "float": float,
    "str": str,
    "len": len,
}
ALLOWED_NODES = (
    ast.Expression,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.Call,
    ast.keyword,
    ast.Subscript,
    ast.List,
    ast.Tuple,
    ast.Slice,
    ast.operator,
    ast.unaryop,
    ast.boolop,
    ast.cmpop,
)


def compile_expression(expression):
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
                raise ValueError("Only the documented numeric and string functions may be called")
    return compile(tree, "<CSV expression>", "eval")


def convert_to_number(value):
    """Convert numeric strings, including scientific notation; preserve other text."""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def calculate_row(expression, row):
    values = [convert_to_number(value) for value in row]
    variables = {f"c{index}": value for index, value in enumerate(values)}
    variables["c"] = values
    return eval(expression, {"__builtins__": {}, **FUNCTIONS}, variables)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: csv_add_column.py data.csv 'c1 * c[-1]' -c total",
    )
    parser.add_argument("input_file", nargs="?", help="Input file; omitted or '-' reads stdin")
    parser.add_argument(
        "expression", help="Expression using c0, c1, ... or c[index], including c[-1]"
    )
    add_csv_options(parser)
    parser.add_argument(
        "-c", "--column-name", help="Name the appended column and treat the first row as a header"
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="Atomically replace the input file"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Report the processed row count to stderr"
    )
    parser.add_argument(
        "--on-error",
        choices=("error", "empty"),
        default="error",
        help="Handle row calculation errors (default: error)",
    )
    args = parse_args(parser, argv)
    if args.in_place and (args.output is not None or not args.input_file or args.input_file == "-"):
        parser.error("--in-place requires an input file and cannot be combined with --output")
    if args.column_name is not None and not args.column_name.strip():
        parser.error("--column-name must not be empty")
    expression = compile_expression(args.expression)
    output_path = args.input_file if args.in_place else args.output
    count = 0
    with open_input(args.input_file, args.encoding) as source:
        reader = csv.reader(source, delimiter=args.delimiter, strict=True)
        first = next(reader, None)
        if first is not None and args.column_name in first:
            raise ValueError(f"Column already exists: {args.column_name}")
        with open_output(output_path, args.output_encoding) as output:
            writer = csv_writer(output, args)
            if first is None:
                return
            if args.column_name is not None:
                writer.writerow(first + [args.column_name])
                records = reader
            else:
                records = chain([first], reader)
            for row in records:
                if len(row) != len(first):
                    raise ValueError(f"Inconsistent row width near input line {reader.line_num}")
                try:
                    value = calculate_row(expression, row)
                except Exception as exc:
                    if args.on_error == "error":
                        raise ValueError(
                            f"Calculation failed near input line {reader.line_num}: {exc}"
                        ) from exc
                    value = ""
                writer.writerow(row + [value])
                count += 1
    if args.verbose:
        print(f"Processed {count} data rows", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
