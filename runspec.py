#!/usr/bin/env python3
# Source: https://github.com/rrwhx/runspec
"""Run SPEC CPU under an optional command prefix.

Two ways to use this module:

* CLI: same flags as before; emits a ``<title>_<spec>_<size>_<stamp>.csv``
  plus a sibling ``.json`` with the structured run result.
* As a library::

      from runspec import Runner
      result = Runner(dir="/path/to/spec",
                      exe="/path/to/exes",
                      benchmark="505",
                      size="test",
                      cmd_prefix="qemu-riscv64 -plugin foo -D %s -- ",
                      intfp=True).run()
      for b in result["benchmarks"]:
          print(b["name"], b["logs"])

  ``result`` matches the JSON file: ``spec_version``, ``size``, ``tune``,
  ``log_dir``, ``csv_path``, ``json_path``, ``benchmarks`` (each with
  ``reftime``, ``runtime``, ``ratio``, ``exit_code``, ``logs``, ``cmds``,
  ``work_dir``), ``geomean``, ``exit_code``.
"""
import argparse
import glob
import json
import math
import os
import re
import resource
import shlex
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import reduce


_SPEC_LAYOUTS = {
    "2000": {
        "marker": "benchspec/CINT2000",
        "base_subdir": "benchspec",
        "ignore_prefix": ["-u"],
        "CINT": ["164.gzip", "175.vpr", "176.gcc", "181.mcf", "186.crafty",
                 "197.parser", "252.eon", "253.perlbmk", "254.gap", "255.vortex",
                 "256.bzip2", "300.twolf"],
        "CFP":  ["168.wupwise", "171.swim", "172.mgrid", "173.applu", "177.mesa",
                 "178.galgel", "179.art", "183.equake", "187.facerec", "188.ammp",
                 "189.lucas", "191.fma3d", "200.sixtrack", "301.apsi"],
        "INT_NO_FORTRAN": [],
        "FP_NO_FORTRAN": [],
    },
    "2006": {
        "marker": "benchspec/CPU2006",
        "base_subdir": "benchspec/CPU2006",
        "ignore_prefix": ["-C"],
        "CINT": ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk",
                 "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref",
                 "471.omnetpp", "473.astar", "483.xalancbmk"],
        "CFP":  ["410.bwaves", "416.gamess", "433.milc", "434.zeusmp", "435.gromacs",
                 "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII",
                 "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD",
                 "465.tonto", "470.lbm", "481.wrf", "482.sphinx3"],
        "INT_NO_FORTRAN": ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf",
                           "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum",
                           "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk"],
        "FP_NO_FORTRAN": ["433.milc", "444.namd", "447.dealII", "450.soplex",
                          "453.povray", "470.lbm", "482.sphinx3"],
    },
    "2017": {
        "marker": "benchspec/CPU",
        "base_subdir": "benchspec/CPU",
        "ignore_prefix": ["-E", "-r", "-N C", "-C", "-b"],
        "CINT": ["500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r",
                 "523.xalancbmk_r", "525.x264_r", "531.deepsjeng_r", "541.leela_r",
                 "548.exchange2_r", "557.xz_r"],
        "CFP":  ["503.bwaves_r", "507.cactuBSSN_r", "508.namd_r", "510.parest_r",
                 "511.povray_r", "519.lbm_r", "521.wrf_r", "526.blender_r",
                 "527.cam4_r", "538.imagick_r", "544.nab_r", "549.fotonik3d_r",
                 "554.roms_r"],
        "INT_NO_FORTRAN": ["500.perlbench_r", "502.gcc_r", "505.mcf_r",
                           "520.omnetpp_r", "523.xalancbmk_r", "525.x264_r",
                           "531.deepsjeng_r", "541.leela_r", "557.xz_r"],
        "FP_NO_FORTRAN":  ["508.namd_r", "510.parest_r", "511.povray_r",
                           "519.lbm_r", "526.blender_r", "538.imagick_r",
                           "544.nab_r"],
    },
}


def _detect_spec_version(spec_dir):
    for v, info in _SPEC_LAYOUTS.items():
        if os.path.exists(os.path.join(spec_dir, info["marker"])):
            return v
    return None


def _detect_ext(spec_dir):
    exes = glob.glob(os.path.join(spec_dir, "benchspec/*/*/run/run_*.0000"))
    names = {os.path.basename(p) for p in exes}
    return {n.rstrip(".0000").split("_", maxsplit=3)[-1] for n in names}


def _matches(query, candidate, substring=False):
    """Strict-by-default benchmark name match.

    Exact, prefix (``525.x264`` -> ``525.x264_r``), or numeric id alone
    (``505`` -> ``505.mcf_r``). ``substring=True`` restores the legacy
    behaviour where ``505`` would also match ``500.perlbench_r`` etc.
    """
    if substring:
        return query in candidate
    if query == candidate:
        return True
    if candidate.startswith(query + ".") or candidate.startswith(query + "_"):
        return True
    if query.isdigit():
        m = re.match(r"^(\d+)\.", candidate)
        if m and m.group(1) == query:
            return True
    return False


def _waitstatus_to_rc(r):
    """Reduce os.system's encoded wait status to a sane exit code."""
    if r == 0:
        return 0
    try:
        return os.waitstatus_to_exitcode(r) or 1
    except (AttributeError, ValueError):
        return r


def _json_safe(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


class Runner:
    """Reusable SPEC CPU runner.

    Constructor params mirror the CLI flags one-for-one. ``run()`` returns
    a dict with the timing CSV path, JSON path, and per-benchmark records;
    the same content is written to ``<log_dir>.json`` next to ``<log_dir>.csv``.

    For wrappers: prefer ``pre_argv=["qemu", ..., "-D", "{log}", "--"]`` over
    ``cmd_prefix="qemu ... -D %s --"`` — list form avoids shell-quoting bugs.
    Either way, each benchmark's resolved log paths come back in
    ``result["benchmarks"][i]["logs"]`` so callers no longer need to glob.
    """

    def __init__(self, *,
                 dir=".",
                 exe="",
                 benchmark="all",
                 size="test",
                 tune="base",
                 ext="",
                 suffix="",
                 threads=1,
                 redirect_stderr=False,
                 loose=False,
                 dry_run=False,
                 verbose=False,
                 intfp=False,
                 cmd_prefix="",
                 pre_argv=None,
                 title="test_title",
                 stamp="time",
                 result_dir=None,
                 copy_exe=False,
                 dup_exe=False,
                 slimit=-1,
                 match_substring=False):
        self.spec_dir = os.path.abspath(dir)
        self.exe_dir = os.path.abspath(exe) if exe else ""
        self.benchmark_arg = benchmark
        self.size = size                       # user-facing, used for log_dir
        self.tune = tune
        self.suffix = suffix
        self.threads = threads if threads else max(1, (os.cpu_count() - 4) // 2)
        self.redirect_stderr = redirect_stderr
        self.loose = loose
        self.dry_run = dry_run
        self.verbose = verbose
        self.intfp = intfp
        self.cmd_prefix = cmd_prefix
        self.pre_argv = list(pre_argv) if pre_argv else None
        self.title = title
        self.copy_exe = copy_exe
        self.dup_exe = dup_exe
        self.slimit = slimit
        self.match_substring = match_substring

        if self.dry_run:
            self.threads = 1

        if not os.path.exists(self.spec_dir):
            raise FileNotFoundError(
                f"cannot open `{self.spec_dir}' (No such file or directory)")

        self.spec = _detect_spec_version(self.spec_dir)
        if self.spec is None:
            raise ValueError(f"{self.spec_dir} is not a spec cpu dir")

        layout = _SPEC_LAYOUTS[self.spec]
        self.base_dir = os.path.join(self.spec_dir, layout["base_subdir"])
        if not os.path.exists(self.base_dir):
            raise FileNotFoundError(f"{self.base_dir} not existed")

        self.speccmd_ignore_prefix = layout["ignore_prefix"]
        self.CINT = list(layout["CINT"])
        self.CFP = list(layout["CFP"])
        self.INT_NO_FORTRAN = list(layout["INT_NO_FORTRAN"])
        self.FP_NO_FORTRAN = list(layout["FP_NO_FORTRAN"])

        # The 2000 layout has no run_*.0000 files, so ext is meaningless there.
        self.ext = ext
        if not self.ext and self.spec != "2000":
            exts = _detect_ext(self.spec_dir)
            if len(exts) != 1:
                raise RuntimeError(
                    "--ext was not specified, and auto probe failed "
                    f"(found: {sorted(exts)})")
            self.ext = next(iter(exts))

        # Internal "effective" size: 2017 lays out refrate dirs even when the
        # user says -i ref. log_dir keeps the user's spelling.
        self._effective_size = ("refrate"
                                if self.spec == "2017" and self.size == "ref"
                                else self.size)

        if self.spec == "2000":
            self.sub_dir = {"test": "run/00000001",
                            "train": "run/00000002",
                            "ref": "run/00000003"}[self._effective_size]
        elif self.spec == "2006":
            self.sub_dir = f"run/run_base_{self._effective_size}_{self.ext}.0000"
        else:
            self.sub_dir = (f"run/run_{self.tune}_{self._effective_size}_"
                            f"{self.ext}.0000")

        if result_dir is None:
            result_dir = os.path.expanduser("~") + "/runspec_result"
        self.result_dir = result_dir
        os.makedirs(self.result_dir, exist_ok=True)

        self.stamp = (datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                      if stamp == "time" else stamp)
        # Preserves the original log_dir spelling (user-supplied size, not
        # the remapped one) so existing wrappers find the same path.
        self.log_dir = (f"{self.result_dir}/{self.title}_{self.spec}_"
                        f"{self.size}_{self.stamp}")
        self.csv_path = self.log_dir + ".csv"
        self.json_path = self.log_dir + ".json"

        if not self.dry_run and self._cmd_uses_log_dir():
            os.makedirs(self.log_dir, exist_ok=True)

    # ------------------------------------------------------------------ helpers

    def _cmd_uses_log_dir(self):
        if "%s" in self.cmd_prefix:
            return True
        if self.pre_argv and any("{log}" in a for a in self.pre_argv):
            return True
        if self.redirect_stderr:
            return True
        return False

    def _apply_slimit(self):
        if self.slimit == 0:
            resource.setrlimit(resource.RLIMIT_STACK,
                               (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        elif self.slimit > 0:
            n = self.slimit << 20
            resource.setrlimit(resource.RLIMIT_STACK, (n, n))

    def _dir_prefix(self, benchmark):
        if self.spec == "2000":
            return "CINT2000" if benchmark in self.CINT else "CFP2000"
        return ""

    def _work_dir(self, benchmark):
        return os.path.join(self.base_dir, self._dir_prefix(benchmark),
                            benchmark, self.sub_dir)

    def _reftime_path(self, benchmark):
        return os.path.join(self.base_dir, self._dir_prefix(benchmark),
                            benchmark, f"data/{self._effective_size}/reftime")

    def _get_reftime(self, benchmark):
        if (self.spec == "2000" and self._effective_size == "test"
                and benchmark == "172.mgrid"):
            return 1.0
        with open(self._reftime_path(benchmark)) as f:
            line_idx = 0 if self.spec == "2017" else 1
            parts = f.readlines()[line_idx].strip().split()
        if self.spec == "2017" and self._effective_size == "refrate":
            assert parts[0] == "refrate"
        return float(parts[-1])

    def _intfp_prefix(self, benchmark):
        if not self.intfp:
            return ""
        return self._score_type(benchmark) + "-"

    def _score_type(self, benchmark):
        return "int" if benchmark in self.CINT else "xfp"

    def _log_path(self, benchmark, index):
        return (f"{self.log_dir}/{self._intfp_prefix(benchmark)}"
                f"{benchmark}_{index}{self.suffix}")

    def _build_prefix(self, logfile):
        if self.pre_argv is not None:
            resolved = [a.replace("{log}", logfile) for a in self.pre_argv]
            return (shlex.join(resolved) + " ") if resolved else ""
        if "%s" in self.cmd_prefix:
            return self.cmd_prefix.replace("%s", logfile)
        if not self.cmd_prefix:
            return ""
        return self.cmd_prefix + " "

    def _build_cmds(self, benchmark, speccmds_filename):
        with open(speccmds_filename) as f:
            lines = f.readlines()
        cmds = []
        logs = []
        index = 0
        for line in lines:
            if any(line.startswith(p) for p in self.speccmd_ignore_prefix):
                continue
            index += 1
            cmd_args = line[:-1].split(" ")
            i = 0
            stdin = stdout = stderr = ""
            while i < len(cmd_args):
                if cmd_args[i] == "-i":
                    stdin = cmd_args[i + 1]; i += 2
                elif cmd_args[i] == "-o":
                    stdout = cmd_args[i + 1]; i += 2
                elif cmd_args[i] == "-e":
                    stderr = cmd_args[i + 1]; i += 2
                else:
                    break
            cmd = " ".join(cmd_args[i:])
            if self.spec == "2017":
                # 2017 appends `< in > out 2>> err` to the command line; strip.
                for j in range(len(cmd)):
                    if cmd[j] in ('>', '<', '2>>'):
                        cmd = cmd[:j]
                        break
            if self.exe_dir:
                cmd_sp = cmd.strip().split()
                basename = os.path.basename(cmd_sp[0])
                if "_base" in basename:
                    benchname = basename[:basename.find("_base")]
                elif "_peak" in basename:
                    benchname = basename[:basename.find("_peak")]
                else:
                    raise RuntimeError(f"{basename} has not _base and _peak")
                realpath_exe = glob.glob(os.path.join(
                    self.exe_dir, benchname + "*"))[0]
                if self.copy_exe:
                    shutil.copy2(realpath_exe,
                                 os.path.dirname(speccmds_filename))
                    cmd = " ".join(["./" + os.path.basename(realpath_exe)]
                                   + cmd_sp[1:])
                else:
                    cmd = " ".join([realpath_exe] + cmd_sp[1:])
            if self.dup_exe:
                cmd = cmd.strip().split()[0] + " " + cmd
            logfile = self._log_path(benchmark, index)
            logs.append(logfile)
            if self.redirect_stderr:
                stderr = logfile + ".stderr"
            prefix = self._build_prefix(logfile)
            full = " ".join([prefix, cmd,
                             f"<{stdin}" if stdin else "",
                             f"1>{stdout}" if stdout else "",
                             f"2>{stderr}" if stderr else ""])
            cmds.append(full)
        return cmds, logs

    def _select(self):
        """Resolve ``-b`` argument to a deduped, ordered benchmark list."""
        keywords = {
            "int":            self.CINT,
            "fp":             self.CFP,
            "all":            self.CINT + self.CFP,
            "int_no_fortran": self.INT_NO_FORTRAN,
            "fp_no_fortran":  self.FP_NO_FORTRAN,
            "no_fortran":     self.INT_NO_FORTRAN + self.FP_NO_FORTRAN,
        }
        selected = []
        seen = set()

        def add(items):
            for it in items:
                if it not in seen:
                    seen.add(it)
                    selected.append(it)

        for tok in self.benchmark_arg.split(","):
            tok = tok.strip()
            if not tok:
                continue
            if tok in keywords:
                add(keywords[tok])
                continue
            add([b for b in self.CINT + self.CFP
                 if _matches(tok, b, substring=self.match_substring)])
        return selected

    # ------------------------------------------------------------------ run

    def run_single(self, benchmark):
        """Run one benchmark sequentially; returns a result dict."""
        work_dir = self._work_dir(benchmark)
        if not os.path.exists(work_dir):
            raise FileNotFoundError(f"{work_dir} not existed")
        cmds, logs = self._build_cmds(
            benchmark, os.path.join(work_dir, "speccmds.cmd"))
        reftime = self._get_reftime(benchmark)

        # Save+restore cwd so callers don't inherit the benchmark's run dir.
        original_cwd = os.getcwd()
        os.chdir(work_dir)
        begin = time.time()
        exit_code = 0
        try:
            for cmd in cmds:
                if self.dry_run or self.verbose:
                    print(f"cd {work_dir} && {cmd}")
                if not self.dry_run:
                    r = os.system(cmd)
                    rc = _waitstatus_to_rc(r)
                    if rc:
                        print(f"error {benchmark}, return value:{r}")
                        print(f"work_dir {work_dir}")
                        print(f"cmd {cmd}")
                        exit_code = rc
                        if not self.loose:
                            break
        finally:
            os.chdir(original_cwd)
        runtime = time.time() - begin
        ratio = (reftime / runtime) if runtime > 0 else float("nan")
        return {
            "name": benchmark,
            "score_type": self._score_type(benchmark),
            "reftime": reftime,
            "runtime": runtime,
            "ratio": ratio,
            "exit_code": exit_code,
            "logs": logs,
            "cmds": cmds,
            "work_dir": work_dir,
        }

    def _run_st(self, selected):
        results = []

        # 按 score_type 分组
        int_benchmarks = [b for b in selected if self._score_type(b) == "int"]
        xfp_benchmarks = [b for b in selected if self._score_type(b) == "xfp"]

        # 执行 INT benchmarks
        if int_benchmarks:
            for b in int_benchmarks:
                r = self.run_single(b)
                results.append(r)
                if not self.dry_run:
                    print("%20s\t%.1f\t%.3f\t%.3f" %
                          (r["name"], r["reftime"], r["runtime"], r["ratio"]))
                if r["exit_code"] and not self.loose:
                    return results

            # INT 完成后立即打印 INT score
            if not self.dry_run:
                int_ratios = self._valid_ratios(results)
                if int_ratios:
                    int_score = self._geomean_from_ratios(int_ratios)
                    print("int score : %.3f" % int_score)

        # 执行 FP benchmarks
        if xfp_benchmarks:
            for b in xfp_benchmarks:
                r = self.run_single(b)
                results.append(r)
                if not self.dry_run:
                    print("%20s\t%.1f\t%.3f\t%.3f" %
                          (r["name"], r["reftime"], r["runtime"], r["ratio"]))
                if r["exit_code"] and not self.loose:
                    return results

            # FP 完成后立即打印 FP score
            if not self.dry_run:
                xfp_results = [r for r in results if r["score_type"] == "xfp"]
                xfp_ratios = self._valid_ratios(xfp_results)
                if xfp_ratios:
                    xfp_score = self._geomean_from_ratios(xfp_ratios)
                    print("xfp score : %.3f" % xfp_score)

        return results

    def _run_mt(self, selected):
        # Build per-benchmark cmds first, then flatten into a task list.
        bench_info = {}
        all_tasks = []  # list of (benchmark, work_dir, raw_cmd, full_task_str)
        for b in selected:
            work_dir = self._work_dir(b)
            if not os.path.exists(work_dir):
                raise FileNotFoundError(f"{work_dir} not existed")
            cmds, logs = self._build_cmds(
                b, os.path.join(work_dir, "speccmds.cmd"))
            reftime = self._get_reftime(b)
            bench_info[b] = {
                "name": b, "score_type": self._score_type(b),
                "reftime": reftime, "runtime": 0.0,
                "ratio": float("nan"), "exit_code": 0,
                "logs": logs, "cmds": cmds, "work_dir": work_dir,
            }
            for c in cmds:
                all_tasks.append((b, work_dir, c, f"cd {work_dir} && {c}"))

        # The h264 2-pass workaround from the original: run pass-2 after
        # pass-1 succeeds. Preserved as-is.
        h264_1 = ("--pass 1 --stats x264_stats.log --bitrate 1000 --frames 1000"
                  " -o BuckBunny_New.264 BuckBunny.yuv 1280x720")
        h264_2 = ("--pass 2 --stats x264_stats.log --bitrate 1000 --dumpyuv 200"
                  " --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720")
        tasks_a = [t for t in all_tasks if h264_2 not in t[3]]
        if any(h264_2 in t[3] for t in all_tasks):
            print("detected h264_2_2017")

        def _run(task_tuple):
            _, _, _, task_str = task_tuple
            t0 = time.time()
            r = os.system(task_str)
            return r, time.time() - t0

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(_run, t): t for t in tasks_a}
            while futures:
                done = next(as_completed(futures))
                task_tuple = futures.pop(done)
                b, work_dir, _c, task_str = task_tuple
                try:
                    print(task_str)
                    r, elapsed = done.result()
                    rc = _waitstatus_to_rc(r)
                    if b in bench_info:
                        bench_info[b]["runtime"] += elapsed
                        if rc:
                            bench_info[b]["exit_code"] = rc
                    if rc:
                        print(f"FAIL:{task_str}")
                    else:
                        print(f"SUCCESS:{task_str}")
                    if h264_1 in task_str and not rc:
                        follow = (b, work_dir, h264_2, h264_2)
                        futures[executor.submit(_run, follow)] = follow
                        print("2017 : Submitted h264_2 after h264_1")
                except Exception as e:
                    print(f"Task {task_str} failed: {e}")

        for info in bench_info.values():
            if info["runtime"] > 0 and not math.isnan(info["reftime"]):
                info["ratio"] = info["reftime"] / info["runtime"]
        return list(bench_info.values())

    @staticmethod
    def _valid_ratios(results):
        return [r["ratio"] for r in results
                if r["ratio"] is not None
                and not math.isnan(r["ratio"])
                and r["ratio"] > 0]

    @staticmethod
    def _geomean_from_ratios(ratios):
        if not ratios:
            return None
        return reduce(lambda x, y: x * y, ratios) ** (1.0 / len(ratios))

    def _score_groups(self, results):
        int_results = [r for r in results if r["name"] in self.CINT]
        fp_results = [r for r in results if r["name"] in self.CFP]
        groups = []
        if int_results:
            groups.append(int_results)
        if fp_results:
            groups.append(fp_results)
        return groups

    # ------------------------------------------------------------------ output

    def _write_csv(self, results):
        with open(self.csv_path, "w") as f:
            for group_results in self._score_groups(results):
                for r in group_results:
                    if r["reftime"] is None or r["runtime"] is None:
                        continue
                    f.write("%s,%f,%f,%f\n" % (r["name"], r["reftime"],
                                                r["runtime"], r["ratio"]))
                group_geomean = self._geomean_from_ratios(
                    self._valid_ratios(group_results))
                if group_geomean is not None:
                    f.write("score,,,%s\n" % group_geomean)

    def _write_json(self, payload):
        with open(self.json_path, "w") as f:
            json.dump(_json_safe(payload), f, indent=2)

    def run(self):
        self._apply_slimit()
        if not self.dry_run:
            print("begin : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        selected = self._select()
        results = []
        geomean = None
        error = None

        if not selected:
            error = (f"no benchmarks matched -b {self.benchmark_arg!r} "
                     f"for SPEC {self.spec}")
            print(f"[!] {error}", file=sys.stderr)
        elif self.threads == 1:
            results = self._run_st(selected)
        else:
            results = self._run_mt(selected)

        if results and not self.dry_run:
            ratios = self._valid_ratios(results)
            if ratios:
                geomean = self._geomean_from_ratios(ratios)
                print("score : %.3f" % geomean)

        if not self.dry_run:
            self._write_csv(results)
            print("end   : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        if not results:
            exit_code = 2
        elif any(r["exit_code"] for r in results):
            exit_code = 0 if self.loose else 1
        else:
            exit_code = 0

        int_results = [r for r in results if r["score_type"] == "int"]
        xfp_results = [r for r in results if r["score_type"] == "xfp"]
        int_geomean = self._geomean_from_ratios(self._valid_ratios(int_results))
        xfp_geomean = self._geomean_from_ratios(self._valid_ratios(xfp_results))

        payload = {
            "spec_version": self.spec,
            "size": self.size,
            "tune": self.tune,
            "log_dir": self.log_dir,
            "csv_path": self.csv_path,
            "json_path": self.json_path,
            "benchmarks": results,
            "geomean": geomean,
            "int_geomean": int_geomean,
            "xfp_geomean": xfp_geomean,
            "exit_code": exit_code,
        }
        if error is not None:
            payload["error"] = error
        if not self.dry_run:
            self._write_json(payload)
        return payload


# --------------------------------------------------------------------- CLI

def _make_parser():
    p = argparse.ArgumentParser(
        description=(
            "Run spec cpu with prefix(none, qemu, perf, pin, dynamorio, "
            "strace, time), get log or performance,\n"
            "Spec run directory should be prepared carefully,\n"
            "Run test, train and ref in spec directory(00), or just -a "
            "setup(06,17), "),
        formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('-i', '--size', default="test",
                   choices=['test', 'train', 'ref', 'refrate'])
    p.add_argument('-b', '--benchmark', default="all",
                   help="benchmark selection, all/int/fp, comma separated items")
    p.add_argument('-T', '--tune', default="base", choices=['base', 'peak'])
    p.add_argument('--ext', default="", help="auto probe, need not set")
    p.add_argument('--suffix', default="", help="suffix of output file")
    p.add_argument('-t', '--threads', default=1, type=int,
                   help="Allow N jobs at once;")
    p.add_argument('--redirect_stderr', action='store_true',
                   help="redirect stderr to logfile.stderr")
    p.add_argument('-l', '--loose', action='store_true', help="ignore errors")
    p.add_argument('-n', '--dry_run', action='store_true',
                   help="Don't actually run any cmd; just print them.")
    p.add_argument('-v', '--verbose', action='store_true',
                   help="Print cmd before exec cmd")
    p.add_argument('--intfp', action='store_true', help="intfp prefix")
    p.add_argument('-c', '--cmd_prefix', default='',
                   help=(r'cmd prefix before real cmd, %%s for output, '
                         r'eg: -c "perf stat -o %%s "'))
    p.add_argument('--title', default="test_title")
    p.add_argument('--stamp', default="time")
    p.add_argument('--result_dir',
                   default=os.path.expanduser('~') + '/runspec_result',
                   help="location of cmd_prefix logs, defaults to "
                        "~/runspec_result")
    p.add_argument('--dir', default=".")
    p.add_argument('--exe', default="", help="spec cpu exe dir")
    p.add_argument('--copy_exe', action="store_true",
                   help="copy exe to run dir, used for perlbench test")
    p.add_argument('--dup_exe', action='store_true',
                   help="dup argv[0], used for some bt")
    p.add_argument('--slimit', type=int, default=-1,
                   help="The limit of the stack size, 0 ulimited, or a "
                        "number(MB), default: not modified")
    p.add_argument('--match-substring', dest='match_substring',
                   action='store_true',
                   help="legacy substring match for -b (default: exact / "
                        "prefix / numeric-id)")
    return p


def _cli():
    args = _make_parser().parse_args()
    print(args, file=sys.stderr)
    try:
        runner = Runner(
            dir=args.dir, exe=args.exe, benchmark=args.benchmark,
            size=args.size, tune=args.tune, ext=args.ext,
            suffix=args.suffix, threads=args.threads,
            redirect_stderr=args.redirect_stderr, loose=args.loose,
            dry_run=args.dry_run, verbose=args.verbose,
            intfp=args.intfp, cmd_prefix=args.cmd_prefix,
            title=args.title, stamp=args.stamp,
            result_dir=args.result_dir, copy_exe=args.copy_exe,
            dup_exe=args.dup_exe, slimit=args.slimit,
            match_substring=args.match_substring,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(str(e))
        sys.exit(1)
    print("log dir is %s" % runner.log_dir, file=sys.stderr)
    payload = runner.run()
    sys.exit(payload["exit_code"])


if __name__ == "__main__":
    _cli()
