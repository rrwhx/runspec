#!/usr/bin/python3
import os
import time
from datetime import datetime
from functools import reduce
from multiprocessing import Pool
# import shutil
# import resource
# resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


# runspec config
SPEC = "2006" # "2000"/"2006"/"2017"
SIZE = "ref"  # "test"/"train"/"ref"
# only 2017
TUNE = "base" # "base"/"peak"
# 0: max, 1: single_thread, other: other
THREADS = 1
ignore_error = False
print_cmd_only = True

# prefix config
# cmd_prefix = "/home/lxy/instrument/pin-3.22/pin -t /home/lxy/instrument/pin_tool/DynAveBlkSIZE/obj-intel64/DynAveBlkSIZE.so "
# cmd_prefix = "/home/lxy/bt/qemu-6.2.0/build/qemu-x86_64 "
cmd_prefix = "taskset -c 8 perf stat -o %s /home/lxy/instrument/DynamoRIO-Linux-9.0.1/bin64/drrun -- "
# cmd_prefix = ""
title = "perf_drrun"
log_dir = "/home/lxy/spec/%s_%s_%s_%s/" % (SPEC, SIZE, title, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

#spec cpu diectory
SPEC2000_DIR = "/home/lxy/SPEC/SPEC2000/lxy/spec2000_i386_x87_run"
SPEC2006_DIR = "/home/lxy/SPEC/SPEC2006/lxy/spec2006_x64_sse2"
SPEC2006_EXT = "Ofast_static_x64"
SPEC2017_DIR = "/home/lxy/SPEC/SPEC2017/cpu2017v118_x86_64_v1_run"
SPEC2017_EXT = "mytest"

# DO NOT EDIT FOLLOWING
# log_dir is uniq, need not clean
# os.makedirs(log_dir, exist_ok=True)
# shutil.rmtree(log_dir)
os.makedirs(log_dir, exist_ok=True)

assert SIZE in ["test", "train", "ref"]
if SPEC == "2000":
    # AAAAA
    base_dir = SPEC2000_DIR+ "/benchspec"
    sub_dir = {"test": "run/00000001", "train":"run/00000002", "ref":"run/00000003"}[SIZE]

    speccmd_ignore_prefix = ["-u"]
    CINT = ["164.gzip", "175.vpr", "176.gcc", "181.mcf", "186.crafty", "197.parser", "252.eon", "253.perlbmk", "254.gap", "255.vortex", "256.bzip2", "300.twolf"]
    CFP = ["168.wupwise", "171.swim", "172.mgrid", "173.applu", "177.mesa", "178.galgel", "179.art", "183.equake", "187.facerec", "188.ammp", "189.lucas", "191.fma3d", "200.sixtrack", "301.apsi"]
elif SPEC == "2006":
    # AAAAA
    base_dir = SPEC2006_DIR + "/benchspec/CPU2006"
    sub_dir = "run/run_base_%s_%s.0000" % (SIZE, SPEC2006_EXT)

    speccmd_ignore_prefix = ["-C"]
    CINT = ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk"]
    CFP = ["410.bwaves", "416.gamess", "433.milc", "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII", "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD", "465.tonto", "470.lbm", "481.wrf", "482.sphinx3"]
elif SPEC == "2017":
    # AAAAA
    SIZE = "refrate" if SIZE == "ref" else SIZE
    base_dir = SPEC2017_DIR + "/benchspec/CPU"
    sub_dir = "run/run_%s_%s_%s-m64.0000" % (TUNE, SIZE, SPEC2017_EXT)

    speccmd_ignore_prefix = ["-E", "-r", "-N C", "-C"]
    CINT = ["500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r", "523.xalancbmk_r", "525.x264_r", "531.deepsjeng_r", "541.leela_r", "548.exchange2_r", "557.xz_r"]
    CFP = ["503.bwaves_r", "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r", "519.lbm_r", "521.wrf_r", "526.blender_r", "527.cam4_r", "538.imagick_r", "544.nab_r", "549.fotonik3d_r", "554.roms_r"]
else:
    exit(1)

def get_reftime(reftime_filename, benchmark):
    f = open(reftime_filename)
    if SPEC == "2000" and SIZE == "test" and benchmark == "172.mgrid" :
        return 1.0
    first_line = f.readlines()[0 if SPEC == "2017" else 1].strip().split()
    if SPEC == "2017" and SIZE == "refrate":
        assert first_line[0] == "refrate"
    reftime = float(first_line[-1])
    f.close()
    return reftime

def get_command(benchmark, speccmds_filename):
    f = open(speccmds_filename)
    lines = f.readlines()
    f.close()
    cmds = []
    index = 0
    for line in lines:
        ignore = False
        for prefix in speccmd_ignore_prefix:
            if line.startswith(prefix):
                ignore = True
                break
        if ignore:
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
        if SPEC == "2017":
            for i in range(0, len(cmd)):
                # 2017 append < in > stdout 2>> stderr at end of command
                if cmd[i] in ['>', '<', '2>>'] :
                    cmd = cmd[:i]
                    break
        # print(stdin, stdout, stderr, cmd)
        if "%s" in cmd_prefix:
            cmd_full_prefix = cmd_prefix % (log_dir + "/" + benchmark + str(index))
        elif not cmd_prefix :
            cmd_full_prefix = ""
        else :
            cmd_full_prefix = cmd_prefix + " -- "
        cmd = " ".join([cmd_full_prefix, cmd, ("<"+stdin) if stdin else "", ("1>" +stdout) if stdout else "", ("2>" + stderr) if stderr else ""])
        cmds.append(cmd)
    # print(cmds)
    return cmds

def run_single(benchmark):
    DIR_PREFIX = ""
    if SPEC == "2000" :
        DIR_PREFIX = 'CINT2000' if benchmark in CINT else 'CFP2000'
    work_dir = os.path.join(base_dir, DIR_PREFIX,  benchmark, sub_dir)
    reftime = get_reftime(os.path.join(base_dir, DIR_PREFIX, benchmark, "data/%s/reftime" % (SIZE)), benchmark)
    cmds = get_command(benchmark, os.path.join(work_dir, "speccmds.cmd"))

    os.chdir(work_dir)
    begin = time.time()
    for cmd in cmds:
        if print_cmd_only:
            print("cd %s && %s" % (work_dir, cmd))

        if not print_cmd_only:
            r = os.system(cmd)
            if r:
                print("error %s %d" % (benchmark, r))
                if not ignore_error :
                    exit(r)
    end = time.time()
    runtime = end - begin
    return reftime, runtime, reftime / runtime

def RUN(benchmarks):
    scores = []
    for i in benchmarks:
        reftime, runtime, ratio = run_single(i)
        if not print_cmd_only:
            print("%20s\t%.1f\t%.3f\t%.3f" % (i, reftime, runtime, ratio))
        scores.append(ratio)
    if not print_cmd_only:
        print("score : %.3f" % reduce(lambda x, y: x*y, scores)**(1.0/len(scores)))


def RUN_MT(benchmarks):
    scores = []
    global THREADS
    if not THREADS:
        # do not eat all the threads
        THREADS = (os.cpu_count() - 4) // 2
    with Pool(THREADS) as p:
        r = p.map(run_single, benchmarks)
        for index in range(len(benchmarks)):
            reftime, runtime, ratio = r[index]
            if not print_cmd_only:
                print("%20s\t%.1f\t%.3f\t%.3f" % (benchmarks[index], reftime, runtime, ratio))
            scores.append(ratio)
    if not print_cmd_only:
        print("score : %.3f" % reduce(lambda x, y: x*y, scores)**(1.0/len(scores)))

if not print_cmd_only:
    print("begin : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# if THREADS == 1:
#     RUN(CINT)
#     RUN(CFP)
# else:
#     RUN_MT(CINT)
#     RUN_MT(CFP)

RUN(CINT)
RUN(CFP)

if not print_cmd_only:
    print("end   : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
