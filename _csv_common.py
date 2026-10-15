"""Shared CSV CLI helpers. This module itself only uses the standard library."""

import codecs
import csv
import io
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

AGGREGATIONS = (
    "mean",
    "sum",
    "size",
    "count",
    "min",
    "max",
    "std",
    "var",
    "first",
    "last",
    "median",
    "nunique",
)


def add_csv_options(parser, *, output=True, dataframe=False):
    parser.add_argument("-d", "--delimiter", default=",", help="Input delimiter (default: comma)")
    parser.add_argument("-t", "--tabs", action="store_true", help="Read TSV; overrides -d")
    parser.add_argument("--output-delimiter", default=",", help="Output delimiter (default: comma)")
    parser.add_argument(
        "--encoding", default="utf-8-sig", help="Input encoding (default: UTF-8, optional BOM)"
    )
    parser.add_argument(
        "--output-encoding", default="utf-8", help="Output encoding (default: UTF-8)"
    )
    if output:
        parser.add_argument("-o", "--output", help="Output file; omitted or '-' writes stdout")
    if dataframe:
        parser.add_argument(
            "--string-columns", help="Comma-separated columns to read as text, e.g. id,zip"
        )


def parse_args(parser, argv=None):
    args = parser.parse_args(argv)
    args.delimiter = "\t" if args.tabs else args.delimiter
    for name in ("delimiter", "output_delimiter"):
        value = getattr(args, name)
        if len(value) != 1 or value in "\r\n\0":
            parser.error(
                f"--{name.replace('_', '-')} must be one character other than CR, LF or NUL"
            )
    for name in ("encoding", "output_encoding"):
        try:
            codecs.lookup(getattr(args, name))
        except LookupError:
            parser.error(f"Unknown encoding: {getattr(args, name)}")
    return args


def column_list(value):
    columns = [item.strip() for item in value.split(",")]
    if not all(columns):
        raise ValueError("Column lists must not contain empty names")
    return list(dict.fromkeys(columns))


def require_columns(frame, columns):
    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")


def resolve_columns(selectors, header, width, *, ranges=False):
    indices = []
    for selector in column_list(selectors):
        match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", selector) if ranges else None
        if match:
            start, end = map(int, match.groups())
            if start > end:
                raise ValueError(f"Invalid column range: {selector}")
            selected = range(start, end + 1)
        elif re.fullmatch(r"-?\d+", selector):
            selected = [int(selector)]
        elif header is None:
            raise ValueError(f"Column names require a header: {selector}")
        elif header.count(selector) != 1:
            raise ValueError(f"Column missing or ambiguous: {selector}")
        else:
            selected = [header.index(selector)]
        for index in selected:
            if index < 0 or index >= width:
                raise ValueError(f"Column index {index} outside range 0-{width - 1}")
            if index not in indices:
                indices.append(index)
    return indices


def same_file(left, right):
    if not left or not right or left == "-" or right == "-":
        return False
    return Path(left).resolve() == Path(right).resolve() or (
        Path(left).exists() and Path(right).exists() and os.path.samefile(left, right)
    )


def read_rows(path, *, delimiter=",", encoding="utf-8-sig"):
    """Read CSV records without converting field values."""
    with open_input(path, encoding) as stream:
        return list(csv.reader(stream, delimiter=delimiter, strict=True))


@contextmanager
def _text_stream(stream, encoding):
    if not hasattr(stream, "buffer"):
        yield stream
        return
    wrapper = io.TextIOWrapper(stream.buffer, encoding=encoding, newline="")
    try:
        yield wrapper
    finally:
        wrapper.detach()


@contextmanager
def open_input(path, encoding="utf-8-sig"):
    if path and path != "-":
        with open(path, encoding=encoding, newline="") as stream:
            yield stream
    else:
        with _text_stream(sys.stdin, encoding) as stream:
            yield stream


@contextmanager
def open_output(path, encoding="utf-8"):
    """Replace a file only after writing succeeds; leave existing output on errors."""
    if not path or path == "-":
        with _text_stream(sys.stdout, encoding) as stream:
            yield stream
            stream.flush()
        return
    target = Path(path).resolve()
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            newline="",
            dir=target.parent,
            prefix=".csv-output-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            yield stream
        if target.exists():
            temporary.chmod(target.stat().st_mode & 0o777)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_frame(path, args, *, strings=False):
    import pandas as pd

    text_columns = column_list(args.string_columns) if getattr(args, "string_columns", None) else []
    dtype = str if strings else {col: str for col in text_columns} or None
    # Validate before pandas can infer an index from excess fields or rename
    # duplicate headers. Spooling avoids keeping a second full copy in memory.
    with (
        open_input(path, args.encoding) as stream,
        tempfile.SpooledTemporaryFile(
            mode="w+", encoding="utf-8", newline="", max_size=1024 * 1024
        ) as normalized,
    ):
        reader = csv.reader(stream, delimiter=args.delimiter, strict=True)
        header = next(reader, None)
        if not header:
            raise ValueError("Input must contain a header")
        if len(set(header)) != len(header):
            raise ValueError("Input contains duplicate column names")
        writer = csv.writer(normalized, delimiter=args.delimiter, lineterminator="\n")
        writer.writerow(header)
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f"Inconsistent row width near input line {reader.line_num}")
            writer.writerow(row)
        normalized.seek(0)
        # Literal text such as "NA" is data; only empty fields become missing values.
        frame = pd.read_csv(
            normalized,
            sep=args.delimiter,
            dtype=dtype,
            keep_default_na=False,
            na_values=[] if strings else [""],
        )
    require_columns(frame, text_columns)
    return frame


def write_frame(frame, args):
    with open_output(args.output, args.output_encoding) as stream:
        frame.to_csv(stream, sep=args.output_delimiter, index=False)


def csv_writer(stream, args):
    return csv.writer(stream, delimiter=args.output_delimiter, lineterminator="\n")


def run_cli(main):
    try:
        # The csv module's 128 KiB default is too small for general data exports.
        limit = sys.maxsize
        while True:
            try:
                csv.field_size_limit(limit)
                break
            except OverflowError:
                limit //= 10
        return main() or 0
    except BrokenPipeError:
        # Avoid another BrokenPipeError when Python flushes stdout at shutdown.
        with open(os.devnull, "w") as sink:
            os.dup2(sink.fileno(), sys.stdout.fileno())
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
