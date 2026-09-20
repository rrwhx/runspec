#!/usr/bin/env python3
# Source: https://github.com/rrwhx/runspec
import os
import sys
import argparse
import math

def geomean(xs):
    return math.exp(math.fsum(math.log(x) for x in xs) / len(xs))

def main():
    parser = argparse.ArgumentParser(description="Extract SPEC scores from result log files,\n"
                                     "print a CSV table (one column per log) to stdout.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('inputs', nargs='+', help="SPEC result log files")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print parsed lines and the intermediate dict to stderr")
    args = parser.parse_args()

    print(f"Arguments: {args}", file=sys.stderr)

    r = {}

    for filename in args.inputs:
        print(os.path.basename(filename), file=sys.stderr)
        with open(filename, "r") as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                if "=======================================================================" in line:
                    lines = lines[index + 1:]
                    break
            for index, line in enumerate(lines):
                if "SPEC" in line:
                    lines = lines[:index]
                    break
            g = []
            for line in lines:
                line_sp = line.strip().strip("*").split()
                if not line_sp:
                    continue
                b = line_sp[0]
                s = line_sp[-1]
                if b not in r:
                    r[b] = []
                r[b].append(s)
                g.append(float(s))
                if args.verbose:
                    print(line_sp, file=sys.stderr)
            if "GMEAN" not in r:
                r["GMEAN"] = []
            r["GMEAN"].append(str(geomean(g)))

    if args.verbose:
        print(r, file=sys.stderr)

    print("benchmark", ",".join([os.path.basename(i) for i in args.inputs]), sep=",")
    for k in r.keys():
        print(k, ",".join(r[k]), sep=",")

if __name__ == "__main__":
    main()
