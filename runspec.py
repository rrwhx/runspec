#!/usr/bin/python3
import os
from typing import ByteString
import uuid
import time
from datetime import datetime
from functools import reduce
import shutil
# import resource
# resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

root_dir = os.getcwd()

SPEC = "2006"
size = 'ref'

print_cmd_only = False

if SPEC == "2000":
    base_dir = "/home/lxy/SPEC/SPEC2000/lxy/spec2000_i386_x87_run/benchspec/"
    if size == 'test' :
        sub_dir = "run/00000001"
    elif size == 'train' :
        sub_dir = "run/00000002"
    elif size == 'ref' :
        sub_dir = "run/00000003"
    else :
        os.abort()

    speccmd_ignore_prefix = "-u"
    CINT = ["164.gzip", "175.vpr", "176.gcc", "181.mcf", "186.crafty", "197.parser", "252.eon", "253.perlbmk", "254.gap", "255.vortex", "256.bzip2", "300.twolf"]
    CFP = ["168.wupwise", "171.swim", "172.mgrid", "173.applu", "177.mesa", "178.galgel", "179.art", "183.equake", "187.facerec", "188.ammp", "189.lucas", "191.fma3d", "200.sixtrack", "301.apsi"]
elif SPEC == "2006":
    base_dir = "/home/lxy/SPEC/SPEC2006/lxy/spec2006_x64_sse2/benchspec/CPU2006"
    sub_dir = "run/run_base_%s_Ofast_static_x64.0000" % (size)
    speccmd_ignore_prefix = "-C"
    CINT = ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk"]
    CFP = ["410.bwaves", "416.gamess", "433.milc", "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII", "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD", "465.tonto", "470.lbm", "481.wrf", "482.sphinx3"]
else:
    exit(1)


cmd_prefix = "/home/lxy/instrument/pin-3.22/pin -t /home/lxy/instrument/pin_tool/DynAveBlkSize/obj-intel64/DynAveBlkSize.so "
# cmd_prefix = "/home/lxy/bt/qemu-6.2.0/build/qemu-x86_64 "
# cmd_prefix = "taskset -c 8 perf stat -x , -e duration_time,cpu_core/instructions/ "
title = "dyn_blk_size_pin"
log_dir = "/home/lxy/spec/%s_%s_%s/" % (SPEC, size, title)
os.makedirs(log_dir, exist_ok=True)
shutil.rmtree(log_dir)
os.makedirs(log_dir, exist_ok=True)
# cmd_prefix = ''

def get_reftime(reftime_filename):
    f = open(reftime_filename)
    reftime = float(f.readlines()[1].strip())
    f.close()
    return reftime

def get_command(benchmark, speccmds_filename):
    f = open(speccmds_filename)
    lines = f.readlines()
    f.close()
    cmds = []
    index = 0
    for line in lines:
        if line.startswith(speccmd_ignore_prefix):
            continue
        index += 1
        args = line[:-1].split(" ")
        # print(args)
        i = 0
        stdin = ""
        stdout = ""
        stderr = ""
        while i < len(args) :
            if args[i] == "-i":
                stdin = args[i + 1]
                i += 1
            elif args[i] == "-o":
                stdout = args[i + 1]
                i += 1
            elif args[i] == "-e":
                stderr = args[i + 1]
                i += 1
            else :
                break
            i += 1
        cmd = " ".join(args[i:])
        # print(stdin, stdout, stderr, cmd)
        if cmd_prefix :
            #pin
            cmd_full_prefix = cmd_prefix + " -o %s/%s -- " % (log_dir, benchmark + str(index))
            #qemu
            # cmd_full_prefix = cmd_prefix + " -D %s/%s " % (log_dir, benchmark + str(index))
            #perf
            # cmd_full_prefix = cmd_prefix + " -o %s/%s " % (log_dir, benchmark + str(index))
        else :
            cmd_full_prefix = ""
        cmd = " ".join([cmd_full_prefix, cmd, ("<"+stdin) if stdin else "", ("1>" +stdout) if stdout else "", ("2>" + stderr) if stderr else ""])
        cmds.append(cmd)
    # print(cmds)
    return cmds

def run_single(benchmark):
    DIR_PREFIX = ""
    if SPEC == "2000" :
        DIR_PREFIX = 'CINT2000' if benchmark in CINT else 'CFP2000'
    work_dir = os.path.join(base_dir, DIR_PREFIX,  benchmark, sub_dir)
    reftime = get_reftime(os.path.join(base_dir, DIR_PREFIX, benchmark, "data/ref/reftime"))
    cmds = get_command(benchmark, os.path.join(work_dir, "speccmds.cmd"))

    os.chdir(work_dir)
    begin = time.time()
    for cmd in cmds:
        print("cd %s && %s" % (work_dir, cmd))
        if not print_cmd_only:
            # 100GB
            os.system("ulimit -s 100000000 && " + cmd)
    end = time.time()
    runtime = end - begin
    return reftime, runtime, reftime / runtime

def RUN(benchmarks):
    scores = []
    for i in benchmarks:
        reftime, runtime, ratio = run_single(i)
        if not print_cmd_only:
            print(i, reftime, runtime, ratio)
        scores.append(ratio)
    if not print_cmd_only:
        print("score : ", reduce(lambda x, y: x*y, scores)**(1.0/len(scores)))

if not print_cmd_only:
    print("begin : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
RUN(CINT)
RUN(CFP)
if not print_cmd_only:
    print("end   : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
