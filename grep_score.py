#!/usr/bin/env python3
import os
import sys
import re
import math

def geomean(xs):
    return math.exp(math.fsum(math.log(x) for x in xs) / len(xs))

r = {}

for filename in sys.argv[1:]:
    print(os.path.basename(filename))
    with open (filename, "r") as f:
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
            b = line_sp[0]
            s = line_sp[-1]
            if b not in r:
                r[b] = []
            r[b].append(s)
            g.append(float(s))
            print(line_sp)
        if "GMEAN" not in r:
            r["GMEAN"] = []
        r["GMEAN"].append(str(geomean(g)))

print(r)

print("benchmark", ",".join([os.path.basename(i) for i in sys.argv[1:]]), sep=",")
for k in r.keys():
    print(k, ",".join(r[k]), sep=",")




