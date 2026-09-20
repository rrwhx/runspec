#!/usr/bin/env python3
# Source: https://github.com/rrwhx/runspec
"""Merge several CSV files horizontally or vertically.

Two ways to use this module:

* CLI::

      merge_csv.py a.csv b.csv              # 水平拼接，只保留一个第一列
      merge_csv.py -v a.csv b.csv           # 纵向拼接，只保留一个第一行
      merge_csv.py -k a.csv b.csv           # 保留每个文件的第一列/第一行
      merge_csv.py -u a.csv b.csv           # 去重（水平去重复列，纵向去重复行）
      merge_csv.py -o out.csv a.csv b.csv   # 写文件（默认输出 stdout）

* As a library::

      from merge_csv import merge_csv, merge_horizontal, merge_vertical
      rows = merge_csv(["a.csv", "b.csv"], axis="h")
      rows = merge_vertical(["a.csv", "b.csv"], keep_all=True)

水平拼接时，除第一个文件外其余文件的第一列（通常是 benchmark 名）会被去掉；
纵向拼接时，除第一个文件外其余文件的第一行（通常是表头）会被去掉。
用 keep_all=True / -k 关闭这一去重行为。

dedup=True / -u 开启重复项去除（默认关闭）：水平拼接以各列第一行为 key 去掉重复列，
纵向拼接以各行第一列为 key 去掉重复行，两种方向都只保留首次出现的那一份。
key 为空的列/行不参与去重，避免补空产生的列被误删。

行数（水平）或列数（纵向）不一致时补空串对齐，不截断数据，并在 stderr 告警。
"""
import argparse
import csv
import sys


def read_csv(filename):
    """Read one CSV file into a list of rows; returns [] for an empty file."""
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    except OSError as e:
        raise ValueError(f"读取文件 {filename} 时出错: {e}") from e
    if not rows:
        print(f"警告: 文件 {filename} 为空", file=sys.stderr)
    return rows


def _row_width(rows):
    """Widest row of a file, i.e. the column count it occupies."""
    return max((len(r) for r in rows), default=0)


def _pad(row, width):
    return list(row) + [""] * (width - len(row))


def _dedup_columns(rows):
    """Drop columns whose first-row key already appeared; empty keys are kept."""
    if not rows:
        return rows
    keys = rows[0]
    seen = set()
    keep = []
    for idx, key in enumerate(keys):
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        keep.append(idx)
    if len(keep) == len(keys):
        return rows
    print(f"去重: 丢弃 {len(keys) - len(keep)} 个重复列", file=sys.stderr)
    return [[row[i] if i < len(row) else "" for i in keep] for row in rows]


def _dedup_rows(rows):
    """Drop rows whose first-column key already appeared; empty keys are kept."""
    seen = set()
    kept = []
    for row in rows:
        key = row[0] if row else ""
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        kept.append(row)
    if len(kept) != len(rows):
        print(f"去重: 丢弃 {len(rows) - len(kept)} 个重复行", file=sys.stderr)
    return kept


def merge_horizontal(files, keep_all=False, dedup=False):
    """Concatenate files side by side; returns the merged rows.

    Unless keep_all is set, the first column of every file but the first
    one is dropped, so the merged result keeps a single leading column.
    Files with fewer rows are padded with empty cells instead of
    truncating the longer ones. With dedup, columns sharing a first-row
    key keep only their first occurrence.
    """
    blocks = []
    for idx, filename in enumerate(files):
        rows = read_csv(filename)
        if idx > 0 and not keep_all:
            rows = [row[1:] for row in rows]
        width = _row_width(rows)
        blocks.append([_pad(row, width) for row in rows])
        print(f"正在处理文件: {filename}, {len(rows)} 行 x {width} 列", file=sys.stderr)

    row_counts = [len(b) for b in blocks]
    if len(set(row_counts)) > 1:
        print(f"警告: 文件行数不一致 {dict(zip(files, row_counts))}，缺失处补空",
              file=sys.stderr)

    merged = []
    for i in range(max(row_counts, default=0)):
        row = []
        for block in blocks:
            if i < len(block):
                row.extend(block[i])
            else:
                row.extend([""] * _row_width(block))
        merged.append(row)
    if dedup:
        merged = _dedup_columns(merged)
    return merged


def merge_vertical(files, keep_all=False, dedup=False):
    """Stack files on top of each other; returns the merged rows.

    Unless keep_all is set, the first row of every file but the first one
    is dropped, so the merged result keeps a single header row. Rows are
    padded to the widest column count seen. With dedup, rows sharing a
    first-column key keep only their first occurrence.
    """
    blocks = []
    header = None
    for idx, filename in enumerate(files):
        rows = read_csv(filename)
        if idx == 0:
            header = rows[0] if rows else None
        elif not keep_all and rows:
            if header is not None and rows[0] != header:
                print(f"警告: 文件 {filename} 的第一行与首个文件的表头不同，"
                      f"仍按位置拼接: {rows[0]}", file=sys.stderr)
            rows = rows[1:]
        blocks.append(rows)
        print(f"正在处理文件: {filename}, {len(rows)} 行", file=sys.stderr)

    all_rows = [row for block in blocks for row in block]
    width = _row_width(all_rows)
    widths = {f: _row_width(b) for f, b in zip(files, blocks) if b}
    if len(set(widths.values())) > 1:
        print(f"警告: 文件列数不一致 {widths}，缺失处补空", file=sys.stderr)
    merged = [_pad(row, width) for row in all_rows]
    if dedup:
        merged = _dedup_rows(merged)
    return merged


def merge_csv(files, axis="h", keep_all=False, dedup=False):
    """Merge files along axis 'h' (horizontal) or 'v' (vertical)."""
    if axis in ("h", "horizontal"):
        return merge_horizontal(files, keep_all=keep_all, dedup=dedup)
    if axis in ("v", "vertical"):
        return merge_vertical(files, keep_all=keep_all, dedup=dedup)
    raise ValueError(f"未知的拼接方向: {axis}（可选: h, v）")


def write_csv(rows, output=None):
    """Write rows to output; stdout when output is None."""
    out = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    try:
        csv.writer(out).writerows(rows)
    finally:
        if output:
            out.close()


def _make_parser():
    p = argparse.ArgumentParser(
        prog="merge_csv.py",
        description="Merge several CSV files horizontally or vertically.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "水平拼接(默认)只保留第一个文件的第一列，纵向拼接只保留第一个文件的第一行。\n"
            "行数/列数不一致时补空串对齐，不丢数据。\n\n"
            "Examples:\n"
            "  # 水平拼接，去掉后续文件重复的第一列，输出到 stdout\n"
            "  python merge_csv.py a.csv b.csv > out.csv\n\n"
            "  # 纵向拼接，去掉后续文件重复的表头\n"
            "  python merge_csv.py -v part1.csv part2.csv > all.csv\n\n"
            "  # shell glob 友好\n"
            "  python merge_csv.py -v perf_*.csv > all.csv\n\n"
            "  # 保留每个文件的第一列/第一行\n"
            "  python merge_csv.py -k a.csv b.csv\n\n"
            "  # 水平拼接后按列头去重，只留首次出现的同名列\n"
            "  python merge_csv.py -u a.csv b.csv\n\n"
            "  # 纵向拼接后按 benchmark 名去重，只留首次出现的行\n"
            "  python merge_csv.py -v -u old.csv new.csv\n\n"
            "  # 写到文件而不是 stdout\n"
            "  python merge_csv.py -o out.csv a.csv b.csv\n"
        ),
    )
    p.add_argument("-v", "--vertical", action="store_true",
                   help="纵向拼接，默认水平拼接")
    p.add_argument("-k", "--keep-all", dest="keep_all", action="store_true",
                   help="保留每个文件的第一列(水平)/第一行(纵向)，默认只保留第一个文件的")
    p.add_argument("-u", "--dedup", action="store_true",
                   help="去重（默认关闭）：水平时以各列第一行为 key 去重列，"
                        "纵向时以各行第一列为 key 去重行，只留首次出现的")
    p.add_argument("-o", "--output", default=None,
                   help="write to this file instead of stdout")
    p.add_argument("files", nargs="+", help="input CSV files")
    return p


def main():
    parser = _make_parser()
    args = parser.parse_args()
    print(f"Arguments: {args}", file=sys.stderr)
    try:
        rows = merge_csv(args.files, axis="v" if args.vertical else "h",
                         keep_all=args.keep_all, dedup=args.dedup)
        write_csv(rows, args.output)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    dest = args.output if args.output else "stdout"
    print(f"成功输出 {len(rows)} 行合并数据到 {dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
