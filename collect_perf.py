#!/usr/bin/python3
import sys
import os
import argparse


parser = argparse.ArgumentParser(description ="aollect perf output", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', default="result.csv")
parser.add_argument('-e', '--event',  default="instructions,branches")
args = parser.parse_args()

print(args,file=sys.stderr)

result_dir = args.input

event_list = args.event.split(",")
print(event_list)


dir_list = os.listdir(result_dir)
dir_list = [f for f in dir_list if not f.startswith('.')]
dir_list.sort()
print(dir_list)
data_dict = {}
for item in dir_list:
    data_dict[item] = {event:None for event in event_list}
    filename = os.path.join(result_dir, item)
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.replace(',', '').strip()
            for event in event_list:
                if event in line:
                    assert not data_dict[item][event]
                    data_dict[item][event] = line.split()[0]

print(data_dict)
result_filename = args.output
with open(result_filename, "w") as result_file:
    result_file.write("benchmark," + ','.join(event_list) + '\n')
    for item in dir_list:
        row = [item] + [str(data_dict[item][event]) for event in event_list]
        result_file.write(','.join(row) + '\n')


