"""End-to-end regression tests for the general-purpose CSV commands."""

import csv
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = tuple(path.name for path in sorted(ROOT.glob("csv_*.py")))


def rows(text):
    return list(csv.reader(io.StringIO(text)))


class CsvToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def write(self, name, text):
        path = self.work / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_tool(self, tool, *args, data=None, success=True):
        result = subprocess.run(
            [sys.executable, str(ROOT / tool), *map(str, args)],
            input=data,
            capture_output=True,
            text=True,
            cwd=self.work,
            timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_help_from_another_directory(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertIn("usage:", self.run_tool(tool, "--help").stdout)

    def test_extract_names_ranges_and_quoted_multiline_fields(self):
        result = self.run_tool(
            "csv_extract_columns.py",
            "-",
            "-c",
            "name,2-3,0",
            "-C",
            "2",
            data='id,name,value,note\n1,"gcc, base",42,"line1\nline2"\n',
        )
        self.assertEqual(
            rows(result.stdout),
            [
                ["name", "note", "id"],
                ["gcc, base", "line1\nline2", "1"],
            ],
        )
        result = self.run_tool(
            "csv_extract_columns.py", "-H", "-c", "1,0", "-t", data="a\tb\nc\td\n"
        )
        self.assertEqual(rows(result.stdout), [["b", "a"], ["d", "c"]])

    def test_extract_rejects_invalid_selectors_and_in_place_output(self):
        source = self.write("data.csv", "name,value\na,1\n")
        for selector in ("3-1", "missing", "9"):
            with self.subTest(selector=selector):
                self.run_tool("csv_extract_columns.py", source, "-c", selector, success=False)
        self.run_tool("csv_extract_columns.py", source, "-o", source, success=False)
        self.assertEqual(source.read_text(), "name,value\na,1\n")

    def test_eval_chains_functions_and_handles_division_by_zero(self):
        result = self.run_tool(
            "csv_eval.py",
            "-",
            "-o",
            "-",
            "-e",
            "ipc=instructions/cycles",
            "-e",
            "scaled=ipc*2",
            "-e",
            "delta=diff(instructions)",
            "-e",
            "hour=to_datetime(timestamp).dt.hour",
            "-e",
            "day=to_datetime(timestamp).dt.strftime('%Y-%m-%d')",
            data="instructions,cycles,timestamp\n8,4,2026-01-01 03:00:00\n12,0,2026-01-02 04:00:00\n",
        )
        data = list(csv.DictReader(io.StringIO(result.stdout)))
        self.assertEqual(float(data[0]["ipc"]), 2)
        self.assertEqual(float(data[0]["scaled"]), 4)
        self.assertEqual(data[1]["ipc"], "inf")
        self.assertEqual(data[0]["delta"], "")
        self.assertEqual(float(data[1]["delta"]), 4)
        self.assertEqual(data[1]["hour"], "4")
        self.assertEqual(data[0]["day"], "2026-01-01")

    def test_eval_special_column_names_and_errors(self):
        result = self.run_tool(
            "csv_eval.py",
            "-e",
            "twice=`cpu-cycles`*2",
            "-e",
            "root=sqrt(`cpu-cycles`)",
            data="cpu-cycles\n4\n",
        )
        self.assertEqual(rows(result.stdout)[1], ["4", "8", "2.0"])
        result = self.run_tool(
            "csv_eval.py", "-e", "bad=missing+1", data="cycles\n4\n", success=False
        )
        self.assertEqual(result.stdout, "")

    def test_query_filters_groups_and_sorts(self):
        result = self.run_tool(
            "csv_query.py",
            "-",
            "-f",
            "cycles >= 2",
            "-g",
            "bench",
            "-a",
            "cycles:mean",
            "-s",
            "cycles:desc",
            "--limit",
            "1",
            data="bench,cycles\na,1\na,3\nb,8\n",
        )
        self.assertEqual(rows(result.stdout), [["bench", "cycles"], ["b", "8.0"]])

    def test_query_global_aggregation_and_zero_limit(self):
        result = self.run_tool(
            "csv_query.py",
            "-a",
            "_global_agg_dummy_:sum,cycles:min:max",
            data="_global_agg_dummy_,cycles\n5,2\n7,8\n",
        )
        self.assertEqual(
            rows(result.stdout),
            [
                ["_global_agg_dummy__sum", "cycles_min", "cycles_max"],
                ["12", "2", "8"],
            ],
        )
        result = self.run_tool("csv_query.py", "--limit", "0", data="cycles\n1\n")
        self.assertEqual(rows(result.stdout), [["cycles"]])
        self.run_tool("csv_query.py", "--limit", "-1", data="cycles\n1\n", success=False)

    def test_pivot_preserves_numeric_timestamps_and_rejects_duplicates(self):
        data = "timestamp,metric,value\n100,cycles,2\n100,cycles,3\n100,instructions,10\n"
        args = ("-", "-i", "timestamp", "-c", "metric", "-v", "value")
        self.run_tool("csv_pivot.py", *args, data=data, success=False)
        result = self.run_tool("csv_pivot.py", *args, "-a", "sum", data=data)
        self.assertEqual(
            rows(result.stdout),
            [
                ["timestamp", "cycles", "instructions"],
                ["100", "5", "10"],
            ],
        )

    def test_sample_excludes_previous_output_and_deduplicates_paths(self):
        source = self.write("input.csv", "id\n0\n1\n2\n3\n4\n5\n")
        output = self.write("sample.csv", "id\n999\n")
        self.run_tool("csv_sample.py", self.work, source, "-n", "3", "-m", "uniform", "-o", output)
        self.assertEqual(rows(output.read_text()), [["id"], ["0"], ["2"], ["4"]])
        self.run_tool("csv_sample.py", self.work, "-n", "3", "-m", "uniform", "-o", output)
        self.assertEqual(rows(output.read_text()), [["id"], ["0"], ["2"], ["4"]])

    def test_sample_random_reproducibility_and_empty_sample(self):
        data = "id\n" + "".join(f"{i}\n" for i in range(30))
        first = self.run_tool("csv_sample.py", "-n", "6", "--seed", "42", data=data)
        second = self.run_tool("csv_sample.py", "-", "-n", "6", "--seed", "42", data=data)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(len(rows(first.stdout)), 7)
        result = self.run_tool("csv_sample.py", "-r", "0.01", "-m", "uniform", data="id\n1\n")
        self.assertEqual(rows(result.stdout), [["id"]])

    def test_sample_fails_without_writing_partial_output(self):
        source = self.write("good.csv", "id\n1\n")
        output = self.write("result.csv", "original\n")
        bad = self.write("bad.csv", 'id,value\n"unclosed,1\n')
        for other in (self.work / "missing.csv", bad):
            self.run_tool("csv_sample.py", source, other, "-o", output, success=False)
            self.assertEqual(output.read_text(), "original\n")

    def test_split_keeps_distinct_keys_separate_after_filename_sanitizing(self):
        data = "group,host,value\na/b,x,1\na?b,x,2\na_b,x,3\na,b_x,4\n"
        self.run_tool("csv_split_by_column.py", "-", "-c", "group,host", data=data)
        files = sorted((self.work / "out_split").glob("*.csv"))
        self.assertEqual(len(files), 4)
        result = []
        for path in files:
            contents = rows(path.read_text())
            self.assertEqual(contents[0], ["group", "host", "value"])
            self.assertEqual(len(contents), 2)
            result.extend(contents[1:])
        self.assertCountEqual(result, rows(data)[1:])

    def test_split_missing_values_and_no_header(self):
        self.run_tool(
            "csv_split_by_column.py", "-c", "1", "--keep-missing", data="name,group\na\nb,MISSING\n"
        )
        files = sorted((self.work / "out_split").glob("*.csv"))
        self.assertEqual(len(files), 2)
        self.run_tool(
            "csv_split_by_column.py",
            "-H",
            "-c",
            "0",
            "-o",
            ".",
            "--prefix",
            "part_",
            data="a,1\na,2\n",
        )
        self.assertEqual(rows((self.work / "part_a.csv").read_text()), [["a", "1"], ["a", "2"]])
        self.run_tool("csv_split_by_column.py", "-c", "-1", data="x\n1\n", success=False)

    def test_split_cannot_overwrite_input(self):
        source = self.write("part_a.csv", "name,value\na,1\n")
        self.run_tool(
            "csv_split_by_column.py",
            source,
            "-c",
            "name",
            "-o",
            ".",
            "--prefix",
            "part_",
            success=False,
        )
        self.assertEqual(source.read_text(), "name,value\na,1\n")

    def test_random_noise_is_reproducible_and_preserves_other_columns(self):
        data = "cycles,timestamp\n1,100\n2,200\n"
        args = ("-c", "cycles", "-r", "-0.5", "0.5", "--seed", "42")
        first = self.run_tool("csv_add_random.py", *args, data=data)
        second = self.run_tool("csv_add_random.py", "-i", "-", "-o", "-", *args, data=data)
        self.assertEqual(first.stdout, second.stdout)
        result = rows(first.stdout)
        for original, row in zip((1, 2), result[1:]):
            self.assertLessEqual(abs(float(row[0]) - original), 0.5)
            self.assertEqual(row[1], str(original * 100))
        self.run_tool(
            "csv_add_random.py", "-c", "missing", "-r", "0", "1", data=data, success=False
        )

    def test_analysis_pipeline(self):
        data = "product,region,price,quantity\nbook,east,8,4\nbook,west,12,4\npen,east,9,3\n"
        data = self.run_tool("csv_eval.py", "-e", "total=price*quantity", data=data).stdout
        data = self.run_tool("csv_query.py", "-f", 'product == "book"', data=data).stdout
        data = self.run_tool(
            "csv_pivot.py", "-i", "product", "-c", "region", "-v", "total", data=data
        ).stdout
        data = self.run_tool("csv_extract_columns.py", "-c", "product,east,west", data=data).stdout
        self.assertEqual(rows(data), [["product", "east", "west"], ["book", "32", "48"]])

    def test_eval_non_finite_policy_is_explicit(self):
        output = self.write("out.csv", "original\n")
        args = ("-e", "ratio=a/b", "--non-finite")
        data = "a,b\n1,0\n"
        result = self.run_tool("csv_eval.py", *args, "empty", data=data)
        self.assertEqual(rows(result.stdout)[1], ["1", "0", ""])
        self.run_tool("csv_eval.py", *args, "error", "-o", output, data=data, success=False)
        self.assertEqual(output.read_text(), "original\n")
        result = self.run_tool("csv_eval.py", "-e", "delta=diff(a).fillna(0)", data=data)
        self.assertEqual(rows(result.stdout)[1][-1], "0.0")

    def test_common_delimiters_encoding_and_bom(self):
        source = self.work / "input.tsv"
        source.write_bytes("group\tkey\tvalue\n东\ta\t4\n".encode("utf-16"))
        cases = {
            "csv_add_column.py": ["c2 * 2", "-c", "double"],
            "csv_combine.py": ["0", "2", "--skip-header", "--no-header"],
            "csv_merge.py": [],
            "csv_reduce.py": [
                "--key",
                "group",
                "-e",
                "value",
                "--key-mode",
                "exact",
                "--no-group-summary",
            ],
            "csv_eval.py": [],
            "csv_query.py": [],
            "csv_sample.py": [],
            "csv_extract_columns.py": [],
            "csv_pivot.py": ["-i", "group", "-c", "key", "-v", "value"],
            "csv_add_random.py": ["-c", "value", "-r", "0", "0"],
            "csv_split_by_column.py": ["-c", "group"],
        }
        for tool, arguments in cases.items():
            with self.subTest(tool=tool):
                destination = self.work / tool.replace(".py", ".csv")
                self.run_tool(
                    tool,
                    source,
                    *arguments,
                    "-t",
                    "--encoding",
                    "utf-16",
                    "--output-delimiter",
                    ";",
                    "--output-encoding",
                    "utf-16",
                    "-o",
                    destination,
                )
                if tool == "csv_split_by_column.py":
                    destination = next(destination.glob("*.csv"))
                result = list(
                    csv.reader(io.StringIO(destination.read_text(encoding="utf-16")), delimiter=";")
                )
                self.assertEqual(result[0 if tool == "csv_combine.py" else 1][0], "东")
        for tool in ("csv_extract_columns.py", "csv_query.py", "csv_sample.py"):
            result = self.run_tool(tool, data="\ufeffid,value\n001,NA\n")
            self.assertEqual(rows(result.stdout)[0], ["id", "value"])

    def test_sampling_preserves_text_and_supports_non_csv_files(self):
        source = self.write("input.txt", "id\tvalue\n001\tNA\n002\tnull\n003\t1.00\n")
        result = self.run_tool("csv_sample.py", source, "-t", "-n", "3")
        self.assertEqual(
            rows(result.stdout), [["id", "value"], ["001", "NA"], ["002", "null"], ["003", "1.00"]]
        )
        result = self.run_tool("csv_sample.py", self.work, "--pattern", "*.txt", "-t", "-r", "0")
        self.assertEqual(rows(result.stdout), [["id", "value"]])

    def test_sampling_rejects_mismatched_headers(self):
        first = self.write("first.csv", "id,value\n1,2\n")
        second = self.write("second.csv", "value,id\n3,4\n")
        output = self.write("output.csv", "original\n")
        self.run_tool("csv_sample.py", first, second, "-o", output, success=False)
        self.assertEqual(output.read_text(), "original\n")

    def test_query_validates_sort_even_on_empty_results(self):
        for sort in ("missing", "value:descending", "value:"):
            self.run_tool(
                "csv_query.py", "-f", "value > 100", "-s", sort, data="value\n1\n", success=False
            )

    def test_query_preserves_empty_group_keys_and_literal_na(self):
        data = "category,value\n,2\nNA,3\na,4\n"
        result = self.run_tool("csv_query.py", "-g", "category", "-a", "value:sum", data=data)
        self.assertEqual(
            rows(result.stdout), [["category", "value"], ["", "2"], ["NA", "3"], ["a", "4"]]
        )
        result = self.run_tool(
            "csv_query.py", "-g", "category", "-a", "value:sum", "--drop-na-groups", data=data
        )
        self.assertEqual(len(rows(result.stdout)), 3)
        result = self.run_tool("csv_query.py", "-a", "value:count:sum", data="value\n")
        self.assertEqual(rows(result.stdout), [["value_count", "value_sum"], ["0", "0"]])
        result = self.run_tool("csv_query.py", "-g", "category", "-a", "category:count", data=data)
        self.assertEqual(rows(result.stdout)[0], ["category", "category_count"])

    def test_string_columns_and_noise_preserve_identifiers(self):
        data = "id,label,value\n001,NA,4\n"
        result = self.run_tool(
            "csv_eval.py", "--string-columns", "id", "-e", "twice=value*2", data=data
        )
        self.assertEqual(rows(result.stdout)[1], ["001", "NA", "4", "8"])
        result = self.run_tool("csv_add_random.py", "-c", "value", "-r", "0", "0", data=data)
        self.assertEqual(rows(result.stdout)[1], ["001", "NA", "4.0"])

    def test_pivot_keeps_missing_keys_and_checks_output_names(self):
        result = self.run_tool(
            "csv_pivot.py",
            "-i",
            "category",
            "-c",
            "key",
            "-v",
            "value",
            "-a",
            "sum",
            data="category,key,value\n,x,2\na,x,3\n",
        )
        self.assertEqual(len(rows(result.stdout)), 3)
        self.assertIn(["", "2"], rows(result.stdout))
        self.run_tool(
            "csv_pivot.py",
            "-i",
            "category",
            "-c",
            "key",
            "-v",
            "value",
            data="category,key,value\na,category,2\n",
            success=False,
        )

    def test_extract_errors_do_not_destroy_output(self):
        output = self.write("out.csv", "original\n")
        for data, args in [("a,b\n1,2\n", ["-c", "missing"]), ("a,b\n1,2\n3\n", ["-c", "a,b"])]:
            self.run_tool("csv_extract_columns.py", *args, "-o", output, data=data, success=False)
            self.assertEqual(output.read_text(), "original\n")
        result = self.run_tool("csv_extract_columns.py", "--missing", "empty", data="a,b\n1\n")
        self.assertEqual(rows(result.stdout), [["a", "b"], ["1", ""]])

    def test_split_bounded_handles_long_keys_and_rollback(self):
        key = "地区" * 70
        data = f"group,value\n{key},1\nb,2\n{key},3\n"
        self.run_tool(
            "csv_split_by_column.py",
            "-c",
            "group",
            "-o",
            "parts",
            "--max-open-files",
            "1",
            data=data,
        )
        partitions = sorted((self.work / "parts").glob("*.csv"))
        self.assertEqual(len(partitions), 2)
        all_rows = [row for path in partitions for row in rows(path.read_text())[1:]]
        self.assertCountEqual(all_rows, rows(data)[1:])
        snapshot = {path: path.read_bytes() for path in partitions}
        self.run_tool(
            "csv_split_by_column.py",
            "-c",
            "group",
            "-o",
            "parts",
            data='group,value\nb,99\n"invalid\n',
            success=False,
        )
        self.assertEqual({path: path.read_bytes() for path in partitions}, snapshot)
        self.assertFalse(list((self.work / "parts").glob(".csv-split-*")))

    def test_add_column_preserves_csv_and_supports_scientific_numbers(self):
        data = 'id,value,note\n001,1e2," text, with\na newline "\n'
        result = self.run_tool("csv_add_column.py", "-", "c1 / 2", "-c", "half", data=data)
        self.assertEqual(
            rows(result.stdout),
            [
                ["id", "value", "note", "half"],
                ["001", "1e2", " text, with\na newline ", "50.0"],
            ],
        )
        result = self.run_tool("csv_add_column.py", "c0 + c[-1]", data="1,2\n3,4\n")
        self.assertEqual(rows(result.stdout), [["1", "2", "3"], ["3", "4", "7"]])

    def test_add_column_in_place_rolls_back_on_failure(self):
        source = self.write("input.csv", "a,b\n1,2\n3,0\n")
        source.chmod(0o640)
        self.run_tool("csv_add_column.py", source, "c0/c1", "-c", "ratio", "-i", success=False)
        self.assertEqual(source.read_text(), "a,b\n1,2\n3,0\n")
        self.run_tool(
            "csv_add_column.py", source, "c0/c1", "-c", "ratio", "-i", "--on-error", "empty"
        )
        self.assertEqual(
            rows(source.read_text()), [["a", "b", "ratio"], ["1", "2", "0.5"], ["3", "0", ""]]
        )
        self.assertEqual(source.stat().st_mode & 0o777, 0o640)

    def test_add_column_does_not_implicitly_fill_empty_values(self):
        self.run_tool("csv_add_column.py", "-", "c0+1", data='""\n', success=False)
        result = self.run_tool("csv_add_column.py", "-", "int(c0 or 0)+1", data='""\n')
        self.assertEqual(rows(result.stdout), [["", "1"]])

    def test_combine_pads_empty_files_and_unequal_lengths(self):
        empty = self.write("empty.csv", "")
        data = self.write("data.csv", "a,1\nb,2\n")
        shorter = self.write("short.csv", "z\n")
        result = self.run_tool("csv_combine.py", empty, "0", "1", data, "-1", shorter, "0")
        self.assertEqual(
            rows(result.stdout),
            [
                ["empty_col0", "empty_col1", "data_col-1", "short_col0"],
                ["", "", "1", "z"],
                ["", "", "2", ""],
            ],
        )

    def test_combine_missing_fields_and_stdin(self):
        result = self.run_tool("csv_combine.py", "-", "1", "--no-header", data="a,1\nb\n")
        self.assertEqual(rows(result.stdout), [["1"], [""]])
        self.run_tool(
            "csv_combine.py", "-", "1", "--missing", "error", data="a,1\nb\n", success=False
        )
        self.run_tool("csv_combine.py", "-", "0", "-", "1", data="a,b\n", success=False)

    def test_merge_empty_first_file_and_longer_following_file(self):
        empty = self.write("empty.csv", "")
        first = self.write("first.csv", "id,x\na,1\n")
        second = self.write("second.csv", "id,y\na,2\nb,3\n")
        result = self.run_tool("csv_merge.py", empty, first, second)
        self.assertEqual(rows(result.stdout), [["id", "x", "y"], ["a", "1", "2"], ["b", "", "3"]])
        result = self.run_tool("csv_merge.py", "-v", empty, first, first)
        self.assertEqual(rows(result.stdout), [["id", "x"], ["a", "1"], ["a", "1"]])

    def test_merge_rejects_mismatched_keys_or_headers(self):
        first = self.write("first.csv", "id,x\na,1\n")
        second = self.write("second.csv", "id,y\nb,2\n")
        output = self.write("out.csv", "original\n")
        for flags in ([], ["-v"]):
            self.run_tool("csv_merge.py", first, second, *flags, "-o", output, success=False)
            self.assertEqual(output.read_text(), "original\n")
        result = self.run_tool("csv_merge.py", first, second, "--by-position")
        self.assertEqual(rows(result.stdout), [["id", "x", "y"], ["a", "1", "2"]])
        result = self.run_tool("csv_merge.py", first, second, "-k")
        self.assertEqual(rows(result.stdout), [["id", "x", "id", "y"], ["a", "1", "b", "2"]])

    def test_merge_dedup_does_not_drop_a_row_matching_the_header_key(self):
        first = self.write("first.csv", "id,x\nid,1\na,2\n")
        second = self.write("second.csv", "id,x\nid,3\nb,4\n")
        result = self.run_tool("csv_merge.py", first, second, "-v", "-u")
        self.assertEqual(rows(result.stdout), [["id", "x"], ["id", "1"], ["a", "2"], ["b", "4"]])
        result = self.run_tool("csv_merge.py", first, first, "-u")
        self.assertEqual(rows(result.stdout), rows(first.read_text()))

    def test_reduce_preserves_qualified_names_and_numeric_suffix_rules(self):
        data = "name,value\nint_data_set_1,2\nint_data_set_2,3\nxfp_data_set_1,7\n"
        result = self.run_tool("csv_reduce.py", data=data)
        values = {row[0]: float(row[1]) for row in rows(result.stdout)[1:]}
        self.assertEqual(
            values, {"int_data_set": 5, "int_mean": 5, "xfp_data_set": 7, "xfp_mean": 7}
        )
        result = self.run_tool(
            "csv_reduce.py", "--no-group-summary", data="name,value\nitem_alpha,2\nitem_beta,3\n"
        )
        self.assertEqual(
            rows(result.stdout), [["name", "value"], ["item_alpha", "2.0"], ["item_beta", "3.0"]]
        )
        self.assertFalse((self.work / "result.csv").exists())

    def test_reduce_exact_keys_event_selection_and_large_geometric_mean(self):
        data = "label,category,value\nunused,group_1,1e300\ntext,group_1,1e300\n"
        result = self.run_tool(
            "csv_reduce.py",
            "--key",
            "category",
            "--key-mode",
            "exact",
            "-e",
            "value",
            "-r",
            "geometric",
            "-r2",
            "none",
            data=data,
        )
        self.assertEqual(rows(result.stdout)[0], ["category", "value"])
        self.assertEqual(rows(result.stdout)[1][0], "group_1")
        self.assertAlmostEqual(float(rows(result.stdout)[1][1]) / 1e300, 1.0)

    def test_reduce_invalid_values_and_summary_collisions_preserve_output(self):
        output = self.write("out.csv", "original\n")
        cases = [
            ("name,value\na,-1\n", ["-r", "geometric"]),
            ("name,value\na,\n", []),
            ("name,x,y\na,1,2\nb,3\n", []),
            ("name,value\nall_mean_1,2\n", []),
        ]
        for data, args in cases:
            self.run_tool("csv_reduce.py", *args, "-o", output, data=data, success=False)
            self.assertEqual(output.read_text(), "original\n")

    def test_dataframe_tools_reject_silent_schema_changes(self):
        output = self.write("out.csv", "original\n")
        tools = {
            "csv_eval.py": [],
            "csv_query.py": [],
            "csv_add_random.py": ["-c", "value", "-r", "0", "0"],
            "csv_pivot.py": ["-i", "id", "-c", "kind", "-v", "value"],
        }
        for tool, args in tools.items():
            for data in (
                "id,kind,value\n001,x,3,extra\n",
                "id,kind,value\n001,x\n",
                "id,value,value\n001,2,3\n",
            ):
                with self.subTest(tool=tool, data=data):
                    self.run_tool(tool, *args, "-o", output, data=data, success=False)
                    self.assertEqual(output.read_text(), "original\n")

    def test_all_csv_modules_import_without_side_effects(self):
        code = "import importlib; " + "; ".join(
            f"importlib.import_module({Path(tool).stem!r})" for tool in TOOLS
        )
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_standard_library_tools_work_without_site_packages(self):
        for tool in set(TOOLS) - {
            "csv_eval.py",
            "csv_query.py",
            "csv_pivot.py",
            "csv_add_random.py",
        }:
            result = subprocess.run(
                [sys.executable, "-S", str(ROOT / tool), "--help"],
                cwd=self.work,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_large_fields_and_no_header_sampling_width(self):
        value = "x" * 150000
        result = self.run_tool("csv_extract_columns.py", "-c", "value", data=f"value\n{value}\n")
        self.assertEqual(result.stdout.splitlines()[0], "value")
        self.assertEqual(result.stdout.splitlines()[1], value)
        first = self.write("first.csv", "a,1\n")
        second = self.write("second.csv", "b,2,3\n")
        self.run_tool("csv_sample.py", "-H", first, second, success=False)


if __name__ == "__main__":
    unittest.main()
