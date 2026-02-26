#!/usr/bin/env python3
import sys
import os
import argparse
import numpy as np
from scipy.stats import gmean
import math
import statistics


parser = argparse.ArgumentParser(description ="aollect perf output", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('input', help="Input CSV file")
parser.add_argument('-o', '--output', default="result.csv")
parser.add_argument('-e', '--event',  default="instructions,branches")
parser.add_argument('-r', '--reduce',  default="sum", help="arithmetic(mean)、geometric、harmonic(hmean)、median、sum、product、max、min")
parser.add_argument('-r2', '--reduce2', default="mean", help="Second reduce method for groups, default: mean")
args = parser.parse_args()


def arithmetic_mean(nums):
    """算术平均值（Arithmetic Mean）"""
    return sum(nums) / len(nums) if nums else None

def geometric_mean(nums):
    """几何平均值（Geometric Mean）"""
    if not nums:
        return None
    # 注意：几何平均数适用于所有数均为非负的情况
    product = math.prod(nums)
    return product ** (1 / len(nums))

def harmonic_mean(nums):
    """调和平均值（Harmonic Mean）"""
    # statistics.harmonic_mean 对于包含0的数据可能抛出异常
    try:
        return statistics.harmonic_mean(nums)
    except statistics.StatisticsError as e:
        return f"Error: {e}"

def median(nums):
    """中位数（Median）"""
    return statistics.median(nums)

def summation(nums):
    """求和（Sum）"""
    return sum(nums)

def product(nums):
    """连乘积（Product）"""
    return math.prod(nums)

def maximum(nums):
    """最大值（Maximum）"""
    return max(nums)

def minimum(nums):
    """最小值（Minimum）"""
    return min(nums)

methods = {
    "arithmetic": arithmetic_mean,
    "mean": arithmetic_mean,
    "geometric": geometric_mean,
    "hmean": harmonic_mean,
    "harmonic": harmonic_mean,
    "median": median,
    "sum": summation,
    "product": product,
    "max": maximum,
    "min": minimum,
}

def my_reduce(method, nums):

    if method not in methods:
        print(f"不支持的方法 '{method}'。请选择: arithmetic, geometric, harmonic, median, sum, product, max, min.", file=sys.stderr)
        exit(1)

    try:
        result = methods[method](nums)
    except Exception as e:
        print(f"计算时出现错误: {e}", file=sys.stderr)
        result = None
    return result


print(f"Arguments: {args}", file=sys.stderr)

result_file = args.input

r = {}
header = ""

f = open(result_file, "r")
lines = list(f.readlines())
if lines:
    header = lines[0].strip()

for line in lines[1:]:
    line_sp = line.strip().strip(',').split(",")
    benchname = line_sp[0].rsplit("_", 1)[0]
    benchvalues = [float(_) for _ in line_sp[1:]]
    if benchname not in r:
        r[benchname] = []
    r[benchname].append(benchvalues)

r_reduced = {}
for k,v in r.items():
    r_reduced[k] = [my_reduce(args.reduce.lower(), x) for x in zip(*v)]

if args.reduce2:
    # Second reduce by group
    groups = {}
    for k, v in r_reduced.items():
        parts = k.split("-", 1)
        if len(parts) > 1:
            group_name = parts[0]
            sub_name = parts[1]
        else:
            group_name = "all"
            sub_name = k

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append((sub_name, v))

    final_results = {}

    for group_name, items in groups.items():
        group_values = []
        for sub_name, v in items:
            final_results[sub_name] = v
            group_values.append(v)

        if group_values:
            reduce2_name = f"{group_name}_{args.reduce2.lower()}"
            final_results[reduce2_name] = [my_reduce(args.reduce2.lower(), x) for x in zip(*group_values)]
else:
    final_results = r_reduced

result_filename = args.output
with open(result_filename, "w") as result_file:
    if header:
        result_file.write(header + "\n")
    for k, v in final_results.items():
        result_file.write(k + ",")
        result_file.write(",".join(list(map(str, v))))
        result_file.write("\n")
