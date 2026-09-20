#!/usr/bin/env python3
# Source: https://github.com/rrwhx/runspec
import sys
import os
import argparse
import fnmatch
import re

CMDLINE_RE = re.compile(r"Performance counter stats for ['\"](.*)['\"]\s*:")

def parse_perf_lines(lines):
    """Parse one perf stat section and return a dictionary of events."""
    data = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "seconds time elapsed" in line:
            data["seconds time elapsed"] = line.split()[0]
            continue
        if "seconds user" in line:
            data["seconds user"] = line.split()[0]
            continue
        if "seconds sys" in line:
            data["seconds sys"] = line.split()[0]
            continue

        # Remove sampling percentage like (71.34%)
        line = re.sub(r'\(\s*\d+(?:\.\d+)?\s*%\s*\)', '', line).strip()

        parts = line.split('#', 1)

        primary_part = parts[0].strip()
        if primary_part:
            p_parts = primary_part.split()
            if len(p_parts) >= 2:
                val_str = p_parts[0].replace(',', '')
                try:
                    float(val_str)
                    name = p_parts[1]
                    data[name] = val_str
                except ValueError:
                    if p_parts[0] == "<not" and len(p_parts) >= 3 and p_parts[1] in ["supported>", "counted>"]:
                        name = p_parts[2]
                        data[name] = ""

        if len(parts) > 1:
            secondary_part = parts[1].strip()
            if "/sec" in secondary_part:
                continue
            if secondary_part:
                s_parts = secondary_part.replace('%', '').split()
                if len(s_parts) >= 2:
                    try:
                        float(s_parts[0])
                        name = " ".join(s_parts[1:])
                        data[name] = s_parts[0]
                    except ValueError:
                        pass
    return data

def parse_perf_file(filename):
    """Parse a single perf output file, return a list of (cmdline, events),
    one item per 'Performance counter stats for' section."""
    with open(filename, "r") as f:
        lines = f.readlines()

    sections = []   # (cmdline, section_lines)
    cmdline = None
    cur_lines = []
    seen_marker = False
    for line in lines:
        m = CMDLINE_RE.search(line)
        if m:
            if seen_marker:
                sections.append((cmdline, cur_lines))
            seen_marker = True
            cmdline = m.group(1)
            cur_lines = []
        else:
            cur_lines.append(line)
    if seen_marker:
        sections.append((cmdline, cur_lines))
    else:
        # no marker at all: treat the whole file as one section
        sections.append((None, lines))

    return [(cmd, parse_perf_lines(sec_lines)) for cmd, sec_lines in sections]

def strip_ext(name):
    """Remove a single .txt/.log suffix (unlike rstrip, which strips chars)."""
    for suf in (".txt", ".log"):
        if name.endswith(suf):
            return name[:-len(suf)]
    return name

def shorten_prog_name(prog):
    """'./perlbench_r_base.x86_64.gcc16.O3.generic' -> 'perlbench_r'."""
    name = os.path.basename(prog)
    m = re.match(r'^(.*?)(?:_base|_peak)\..*$', name)
    if m:
        return m.group(1)
    return name

def cmd_to_key(cmdline, with_args=False):
    """Derive a benchmark key from the perf 'stats for' command line."""
    parts = cmdline.split()
    if not parts:
        return ""
    key = shorten_prog_name(parts[0])
    if with_args and len(parts) > 1:
        key = key + "_" + "_".join(parts[1:])
    return key.replace(",", ";")

def main():
    parser = argparse.ArgumentParser(description="Collect perf output", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputs', nargs='+', help="Input directory or files containing perf output")
    parser.add_argument('-e', '--event', default="", help="Comma-separated list of events to extract (default: all)")
    parser.add_argument('-m', '--event-match', dest='event_match', default="exact",
                        choices=['exact', 'glob', 'regex'],
                        help="how -e/--event items are matched (default: exact)\n"
                             "exact: literal names, a missing one still yields an empty column\n"
                             "glob : shell wildcards, eg -e '*cache*,branch*' -m glob\n"
                             "regex: python re.search, eg -e 'cache|^branch' -m regex")
    parser.add_argument('-s', '--sort', action='store_true', default=False,
                        help="sort input files by name (default: keep input/directory order)")
    parser.add_argument('-d', '--dir-key', dest='dir_key', action='store_true', default=False,
                        help="prefix key with the immediate directory name (dir-file),\n"
                             "keeps same file name in different dirs as separate rows\n"
                             "(default: records with the same key are merged into one row)")
    parser.add_argument('-k', '--key', dest='key', default='file',
                        choices=['file', 'cmd', 'cmdargs'],
                        help="how to derive the benchmark key of each record (default: file)\n"
                             "file   : file name without .txt/.log extension\n"
                             "cmd    : program name of the \"Performance counter stats for '<cmd>'\"\n"
                             "         line, SPEC style '_base.'/'_peak.' suffixes stripped\n"
                             "cmdargs: like cmd, plus the program arguments\n"
                             "cmd/cmdargs fall back to the file name if no command line is found")
    args = parser.parse_args()

    print(f"Arguments: {args}", file=sys.stderr)

    file_list = []
    for input_path in args.inputs:
        if os.path.isdir(input_path):
            for f in os.listdir(input_path):
                if not f.startswith('.'):
                    file_list.append(os.path.join(input_path, f))
        elif os.path.isfile(input_path):
            file_list.append(input_path)
        else:
            print(f"Warning: Input path '{input_path}' does not exist or is not a file/directory.", file=sys.stderr)

    if not file_list:
        print("Error: No valid input files found.", file=sys.stderr)
        sys.exit(1)

    if args.sort:
        file_list.sort()
    print(f"Files to process: {file_list}", file=sys.stderr)

    data_dict = {}
    all_events = []
    merge_conflicts = 0
    TIME_EVENTS = {"seconds time elapsed", "seconds user", "seconds sys"}

    def register_events(events):
        for event in events:
            if event not in all_events:
                all_events.append(event)

    for filename in file_list:
        for cmdline, data in parse_perf_file(filename):
            if not data:
                print(f"Warning: no perf events found in '{filename}', skipped.", file=sys.stderr)
                continue
            if args.key != 'file' and cmdline:
                base = cmd_to_key(cmdline, with_args=(args.key == 'cmdargs'))
            else:
                if args.key != 'file' and not cmdline:
                    print(f"Warning: no command line found in '{filename}', "
                          "fall back to the file name key.", file=sys.stderr)
                base = strip_ext(os.path.basename(filename))
            if args.dir_key:
                dirname = os.path.basename(os.path.dirname(os.path.abspath(filename)))
                if dirname:
                    base = f"{dirname}-{base}"

            if base in data_dict:
                # same key: same benchmark measured again (e.g. split event sets),
                # merge into the existing row, the first measured value wins
                existing = data_dict[base]
                for ek, ev in data.items():
                    if ek not in existing:
                        existing[ek] = ev
                    elif existing[ek] != ev and ek not in TIME_EVENTS:
                        # e.g. instructions/cycles measured again in each run
                        merge_conflicts += 1
                register_events(data.keys())
                continue
            data_dict[base] = data
            register_events(data.keys())

    if args.event:
        patterns = args.event.split(",")
        if args.event_match == "exact":
            event_list = patterns
        else:
            event_list = []
            for pat in patterns:
                if args.event_match == "glob":
                    matched = [e for e in all_events if fnmatch.fnmatchcase(e, pat)]
                else:
                    try:
                        regex = re.compile(pat)
                    except re.error as e:
                        print(f"Error: invalid regex '{pat}': {e}", file=sys.stderr)
                        sys.exit(1)
                    matched = [e for e in all_events if regex.search(e)]
                if not matched:
                    print(f"Warning: no event matched '{pat}'", file=sys.stderr)
                for e in matched:
                    if e not in event_list:
                        event_list.append(e)
    else:
        event_list = all_events

    if merge_conflicts:
        print(f"Note: {merge_conflicts} conflicting event value(s) ignored during merge, "
              "the first measured value is kept.", file=sys.stderr)
    print(f"Events to extract: {event_list}", file=sys.stderr)
    # print(f"Extracted data: {data_dict}", file=sys.stderr) # Optional: print all data

    result_file = sys.stdout

    try:
        result_file.write("benchmark," + ','.join(e.replace(' ', '_') for e in event_list) + '\n')
        for item, data in data_dict.items():
            row = [item]
            for event in event_list:
                val = data.get(event, "")
                row.append(str(val))
            result_file.write(','.join(row) + '\n')
    finally:
        pass

if __name__ == "__main__":
    main()


