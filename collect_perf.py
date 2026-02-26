#!/usr/bin/env python3
import sys
import os
import argparse
import re

def parse_perf_file(filename):
    """Parse a single perf output file and return a dictionary of events."""
    data = {}
    started = False
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Performance counter stats for"):
                started = True
                continue
            if not started:
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

def main():
    parser = argparse.ArgumentParser(description="Collect perf output", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputs', nargs='+', help="Input directory or files containing perf output")
    parser.add_argument('-e', '--event', default="", help="Comma-separated list of events to extract (default: all)")
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

    file_list.sort()
    print(f"Files to process: {file_list}", file=sys.stderr)

    data_dict = {}
    all_events = []

    for filename in file_list:
        item = os.path.basename(filename).rstrip(".txt").rstrip(".log")
        data = parse_perf_file(filename)
        data_dict[item] = data

        for event in data.keys():
            if event not in all_events:
                all_events.append(event)

    if args.event:
        event_list = args.event.split(",")
    else:
        event_list = all_events

    print(f"Events to extract: {event_list}", file=sys.stderr)
    # print(f"Extracted data: {data_dict}", file=sys.stderr) # Optional: print all data

    result_file = sys.stdout

    try:
        result_file.write("benchmark," + ','.join(event_list) + '\n')
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


