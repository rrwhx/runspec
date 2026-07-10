#!/usr/bin/env python3
# Source: https://github.com/rrwhx/runspec
"""Combine selected columns from several CSV files side by side.

Argument grammar (comma form only):

    file,col[,col...]                 one file, one or more columns
    file1,file2,...,col[,col...]      several files sharing the same columns

Each command-line token is one self-contained group. Within a token each
comma-separated part is classified independently: parts that parse as
integers are column indices, everything else is a file name. Order within
the token does not matter; all files in a token share all its columns.
Examples::

    a.csv,1,2          -> file a.csv, columns 1 and 2
    a.csv,b.csv,1,2    -> files a.csv and b.csv, both columns 1 and 2
    a.csv,1,b.csv,2    -> files a.csv and b.csv, both columns 1 and 2
    a.csv,-1           -> file a.csv, last column (Python-style negative)

Column indices are 0-based and support Python-style negative indices
(``-1`` is the last column). Rows shorter than requested are padded
with empty strings; files with fewer rows are padded to the longest file.

Output goes to stdout with an auto-generated header, unless overridden.
"""
import argparse
import csv
import os
import sys


def parse_token(tok):
    """Parse one token into (files, cols).

    Each comma-separated part is classified independently: parts that parse
    as integers are column indices, everything else is a file name. Order
    within the token does not matter; all files share all columns.
    """
    parts = tok.split(",")
    if len(parts) < 2:
        raise ValueError(f"参数格式错误 '{tok}': 需要 file,col 或 file1,file2,...,col 形式")

    files = []
    cols = []
    for part in parts:
        try:
            cols.append(int(part))
        except ValueError:
            files.append(part)

    if not files:
        raise ValueError(f"参数格式错误 '{tok}': 缺少文件名")
    if not cols:
        raise ValueError(f"参数格式错误 '{tok}': 缺少列索引")
    return files, cols


def parse_items(items):
    """Parse all tokens into a list of (files, cols) groups."""
    return [parse_token(tok) for tok in items]


def read_csv_columns(filename, col_indices):
    print(f"正在处理文件: {filename}, 提取列: {col_indices}", file=sys.stderr)
    try:
        with open(filename, newline="", encoding="utf-8") as csvfile:
            rows = list(csv.reader(csvfile))
    except OSError as e:
        raise ValueError(f"读取文件 {filename} 时出错: {e}") from e

    if not rows:
        print(f"警告: 文件 {filename} 为空", file=sys.stderr)
        return []

    extracted = []
    for row_idx, row in enumerate(rows):
        out_row = []
        for col in col_indices:
            actual = len(row) + col if col < 0 else col
            if 0 <= actual < len(row):
                out_row.append(row[actual])
            else:
                print(f"警告: 文件 {filename} 第 {row_idx + 1} 行没有第 {col} 列",
                      file=sys.stderr)
                out_row.append("")
        extracted.append(out_row)
    print(f"从文件 {filename} 提取了 {len(extracted)} 行数据", file=sys.stderr)
    return extracted


def generate_header(groups):
    header = []
    for files, cols in groups:
        for filename in files:
            basename = os.path.splitext(os.path.basename(filename))[0]
            for col in cols:
                header.append(f"{basename}_col{col}")
    return header


def combine(groups):
    """Return (header, rows) for the given parsed groups."""
    header = generate_header(groups)
    all_data = []
    max_rows = 0
    for files, cols in groups:
        for filename in files:
            data = read_csv_columns(filename, cols)
            all_data.append(data)
            max_rows = max(max_rows, len(data))

    rows = []
    for row_idx in range(max_rows):
        combined = []
        for data in all_data:
            if row_idx < len(data):
                combined.extend(data[row_idx])
            else:
                num_cols = len(data[0]) if data else 0
                combined.extend([""] * num_cols)
        rows.append(combined)
    return header, rows


def _make_parser():
    p = argparse.ArgumentParser(
        prog="combine_csv.py",
        description="Combine selected columns from several CSV files side by side.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Token grammar: file,col[,col...]  or  file1,file2,...,col[,col...]\n\n"
            "Examples:\n"
            "  # one file, columns 1 and 2 (0-based); header + stdout (default)\n"
            "  python combine_csv.py a.csv,1,2 > out.csv\n\n"
            "  # several files sharing one column set\n"
            "  python combine_csv.py a.csv,b.csv,1,2 c.csv,0 > out.csv\n\n"
            "  # last column of each file via negative index\n"
            "  python combine_csv.py a.csv,-1 b.csv,-1 > out.csv\n\n"
            "  # no header, write to a file instead of stdout\n"
            "  python combine_csv.py --no-header -o out.csv a.csv,1,2 b.csv,2\n"
        ),
    )
    p.add_argument("--no-header", action="store_true",
                   help="do not emit the auto-generated header row")
    p.add_argument("-o", "--output", default=None,
                   help="write to this file instead of stdout")
    p.add_argument("items", nargs="+",
                   help="one or more 'file,col[,col...]' tokens")
    return p


def main():
    parser = _make_parser()
    args = parser.parse_args()
    try:
        groups = parse_items(args.items)
        print(f"解析到 {len(groups)} 个文件组", file=sys.stderr)
        header, rows = combine(groups)
        if not args.no_header:
            print("CSV表头: " + ",".join(header), file=sys.stderr)

        out = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout
        try:
            writer = csv.writer(out)
            if not args.no_header:
                writer.writerow(header)
            writer.writerows(rows)
        finally:
            if args.output:
                out.close()

        dest = args.output if args.output else "stdout"
        print(f"成功输出 {len(rows)} 行合并数据到 {dest}", file=sys.stderr)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
