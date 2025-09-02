#!/usr/bin/python3
import sys
import os
import argparse
from math import log, exp

parser = argparse.ArgumentParser(description ="aollect perf output", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', default="result.csv")
parser.add_argument('-e', '--event',  default="instructions,branches")
args = parser.parse_args()

print(args,file=sys.stderr)

result_file = args.input

r = {}

f = open(result_file, "r")
lines = list(f.readlines())
for line in lines[1:]:
    line_sp = line.strip().strip(',').split(",")
    benchname = line_sp[0].split("_")[0]
    benchvalues = [float(_) for _ in line_sp[1:]]
    if benchname not in r:
        r[benchname] = []
    r[benchname].append(benchvalues)
    print(benchname, benchvalues)

r_reduced = {}
for k,v in r.items():
    r_reduced[k] = [sum(x) for x in zip(*v)]

print(r_reduced)

Average = [sum(x) / len(x) for x in zip(*r_reduced.values())]
def geometric_mean(x):
    if any(xi <= 0 for xi in x):
        return 0.0
    return exp(sum(log(xi) for xi in x) / len(x))

GMEAN = [geometric_mean(x) for x in zip(*r_reduced.values())]
Sum = [sum(x) for x in zip(*r_reduced.values())]
r_reduced["Average"] = Average
# r_reduced["GMEAN"] = GMEAN
# r_reduced["Sum"] = Sum
print(list(zip(*list(r_reduced.values()))))

result_filename = args.output
with open(result_filename, "w") as result_file:
    result_file.write(lines[0])
    for k, v in r_reduced.items():
        result_file.write(k + ",")
        result_file.write(",".join(list(map(str, v))))
        result_file.write("\n")





