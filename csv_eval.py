#!/usr/bin/env python3
"""Compute CSV columns from expressions without implicit data cleaning."""

import argparse

import numpy as np
import pandas as pd

from _csv_common import add_csv_options, parse_args, read_frame, run_cli, write_frame

FUNCTIONS = {
    "abs": np.abs,
    "ceil": np.ceil,
    "clip": np.clip,
    "floor": np.floor,
    "log": np.log,
    "log2": np.log2,
    "log10": np.log10,
    "log1p": np.log1p,
    "rint": np.rint,
    "sqrt": np.sqrt,
    "len": len,
    "diff": pd.Series.diff,
    "to_datetime": pd.to_datetime,
}


def parse_expr(expression):
    name, separator, rhs = expression.partition("=")
    name, rhs = name.strip(), rhs.strip()
    if not separator or not name or not rhs:
        raise ValueError(f"Expected NAME=EXPRESSION, got: {expression}")
    return name, rhs


def apply_expressions(frame, expressions, non_finite="keep"):
    created = []
    functions = dict(FUNCTIONS, df=frame)
    for expression in expressions:
        name, rhs = parse_expr(expression)
        try:
            result = frame.eval(rhs, engine="python", parser="pandas", resolvers=[frame, functions])
            if isinstance(result, pd.DataFrame):
                raise ValueError("Expression must return a scalar or a single column")
            if non_finite != "keep":
                values = pd.Series(result, index=frame.index)
                if pd.api.types.is_numeric_dtype(values):
                    infinite = np.isinf(values)
                    if non_finite == "error" and infinite.any():
                        raise ValueError("Expression produced infinite values")
                    if non_finite == "empty":
                        result = values.mask(infinite)
            frame[name] = result
        except Exception as exc:
            raise ValueError(f"Expression {expression!r} failed: {exc}") from exc
        created.append(name)
    return created


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compute CSV columns using pandas expressions.",
        epilog="Example: csv_eval.py sales.csv -e 'total=price*quantity' -e 'change=diff(total)'",
    )
    parser.add_argument("file", nargs="?", help="Input file; omitted or '-' reads stdin")
    add_csv_options(parser, dataframe=True)
    parser.add_argument(
        "-e",
        "--expr",
        action="append",
        default=[],
        metavar="NAME=EXPR",
        help="Repeat to evaluate expressions in order. Functions: " + ", ".join(FUNCTIONS),
    )
    parser.add_argument(
        "--non-finite",
        choices=("keep", "empty", "error"),
        default="keep",
        help="How to handle computed infinities (default: keep)",
    )
    args = parse_args(parser, argv)
    frame = read_frame(args.file, args)
    apply_expressions(frame, args.expr, args.non_finite)
    write_frame(frame, args)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
