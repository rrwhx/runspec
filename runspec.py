#!/usr/bin/python3
import os
import sys
import time
import argparse
import glob
from datetime import datetime
from functools import reduce
from multiprocessing import Pool
import shutil
import resource
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(description =
"""Run spec cpu with prefix(none, qemu, perf, pin, dynamorio, strace, time), get log or performance,
Spec run directory should be prepared carefully,
Run test, train and ref in spec directory(00), or just -a setup(06,17), """, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', '--size', default="test", choices=['test', 'train', 'ref', 'refrate'])
parser.add_argument('-b', '--benchmark', default="all", help="benchmark selection, all/int/fp, comma separated items")
parser.add_argument('-T', '--tune', default="base", choices=['base', 'peak'])
parser.add_argument('--ext', default="", help="auto probe, need not set")
parser.add_argument('--suffix', default="", help="suffix of output file")
parser.add_argument('-t', '--threads', default=1, type=int, help="Allow N jobs at once;")
parser.add_argument('--redirect_stderr', action='store_true', help="redirect stderr to logfile.stderr")
parser.add_argument('-l', '--loose', action='store_true', help="ignore errors")
parser.add_argument('-n', '--dry_run', action='store_true', help="Don't actually run any cmd; just print them.")
parser.add_argument('-v', '--verbose', action='store_true', help="Print cmd before exec cmd")
parser.add_argument('--intfp', action='store_true', help="intfp prefix")
parser.add_argument('-c', '--cmd_prefix', default='', help=r'cmd prefix before real cmd, %%s for output, eg: -c "perf stat -o %%s "')
parser.add_argument('--title', default="test_title")
parser.add_argument('--stamp', default="time")
parser.add_argument('--result_dir', default=os.path.expanduser('~') + '/runspec_result', help="location of cmd_prefix logs, defaults to ~/runspec_result")
parser.add_argument('--dir', default=".")
parser.add_argument('--exe', default="", help="spec cpu exe dir")
parser.add_argument('--copy_exe', action="store_true", help="copy exe to run dir, used for perlbench test")
parser.add_argument('--dup_exe', action='store_true', help="dup argv[0], used for some bt")
parser.add_argument('--slimit', type=int, default=-1,help="The limit of the stack size, 0 ulimited, or a number(MB), default: not modified")
args = parser.parse_args()

print(args,file=sys.stderr)

slimit = args.slimit
if slimit == 0:
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
elif slimit > 0:
    slimit <<= 20
    resource.setrlimit(resource.RLIMIT_STACK, (slimit, slimit))



# runspec config
SIZE = args.size
# only 2017
TUNE = args.tune # "base"/"peak"
# 0: max, 1: single_thread, other: other
THREADS = args.threads
ignore_error = args.loose
dry_run = args.dry_run
verbose = args.verbose

# print cmd by order
if dry_run:
    THREADS = 1

# prefix config
# cmd_prefix = "/home/lxy/instrument/pin-3.24/pin -t /home/lxy/instrument/x86_indirect_branch_analysis/TraceInsImm/obj-intel64/TraceInsImm.so -o %s -- "
# cmd_prefix = "/home/lxy/bt/qemu-6.2.0/build/qemu-x86_64 "
# cmd_prefix = "taskset -c " + cpu + " perf stat -o %s "
# cmd_prefix = "taskset -c 8 perf stat -e cycles,instructions,L1-dcache-loads,L1-dcache-load-misses,r2012,dTLB-load-misses -o %s "
# cmd_prefix = "/bin/qemu-aarch64 -plugin /home/lxy/bt/qemu-plugins_cpp/libbbv.so -d plugin -D %s "
cmd_prefix = args.cmd_prefix

title = args.title
result_dir = args.result_dir

#spec cpu diectory
SPEC_DIR = os.path.abspath(args.dir)
EXE_DIR = os.path.abspath(args.exe) if args.exe else ""
if not os.path.exists(SPEC_DIR):
    print("cannot open `%s' (No such file or directory)" % SPEC_DIR)
    exit(1)

EXE_EXT = args.ext
if not EXE_EXT:
    try:
        exes = glob.glob(os.path.join(SPEC_DIR, "benchspec/*/*/run/run_*.0000"))
        exe_name = set([os.path.basename(_) for _ in exes])
        exe_name_ext = set([_.rstrip(".0000").split("_", maxsplit=3)[-1] for _ in exe_name])
        if len(exe_name_ext) != 1:
            print("multiple exe name ext found, please specify --ext", exe_name_ext)
            exit(1)
        EXE_EXT = exe_name_ext.pop()
        # exe_name.split(base)
    except Exception:
        print("--ext was not specified, and auto probe failed")
        exit(1)
if os.path.exists(os.path.join(SPEC_DIR, "benchspec/CINT2000")):
    SPEC = "2000"
elif os.path.exists(os.path.join(SPEC_DIR, "benchspec/CPU2006")):
    SPEC = "2006"
elif os.path.exists(os.path.join(SPEC_DIR, "benchspec/CPU")):
    SPEC = "2017"
else:
    print("%s is not a spec cpu dir" % SPEC_DIR)
    exit(1)

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

stamp   = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") if args.stamp == 'time' else args.stamp

ensure_directory_exists(result_dir)
log_dir = "%s/%s_%s_%s_%s" % (result_dir, title, SPEC, SIZE, stamp)

print("log dir is %s" % log_dir,file=sys.stderr)

# DO NOT EDIT FOLLOWING
if not dry_run and "%s" in cmd_prefix:
    os.makedirs(log_dir, exist_ok=True)

if not THREADS:
    # do not eat all the threads
    THREADS = (os.cpu_count() - 4) // 2

if SPEC == "2000":
    # AAAAA
    base_dir = SPEC_DIR+ "/benchspec"
    sub_dir = {"test": "run/00000001", "train":"run/00000002", "ref":"run/00000003"}[SIZE]

    speccmd_ignore_prefix = ["-u"]
    CINT = ["164.gzip", "175.vpr", "176.gcc", "181.mcf", "186.crafty", "197.parser", "252.eon", "253.perlbmk", "254.gap", "255.vortex", "256.bzip2", "300.twolf"]
    CFP = ["168.wupwise", "171.swim", "172.mgrid", "173.applu", "177.mesa", "178.galgel", "179.art", "183.equake", "187.facerec", "188.ammp", "189.lucas", "191.fma3d", "200.sixtrack", "301.apsi"]
elif SPEC == "2006":
    # AAAAA
    base_dir = SPEC_DIR + "/benchspec/CPU2006"
    sub_dir = "run/run_base_%s_%s.0000" % (SIZE, EXE_EXT)

    speccmd_ignore_prefix = ["-C"]
    CINT = ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk"]
    CFP = ["410.bwaves", "416.gamess", "433.milc", "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII", "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD", "465.tonto", "470.lbm", "481.wrf", "482.sphinx3"]
#    CFP = ["410.bwaves", "433.milc", "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "447.dealII", "450.soplex", "453.povray", "454.calculix", "459.GemsFDTD", "465.tonto", "470.lbm", "481.wrf", "482.sphinx3"]
    INT_NO_FORTRAN = ["400.perlbench", "401.bzip2", "403.gcc", "429.mcf", "445.gobmk", "456.hmmer", "458.sjeng", "462.libquantum", "464.h264ref", "471.omnetpp", "473.astar", "483.xalancbmk"]
    FP_NO_FORTRAN = ["433.milc", "444.namd", "447.dealII", "450.soplex", "453.povray", "470.lbm", "482.sphinx3"]
elif SPEC == "2017":
    # AAAAA
    SIZE = "refrate" if SIZE == "ref" else SIZE
    base_dir = SPEC_DIR + "/benchspec/CPU"
    sub_dir = "run/run_%s_%s_%s.0000" % (TUNE, SIZE, EXE_EXT)

    speccmd_ignore_prefix = ["-E", "-r", "-N C", "-C", "-b"]
    CINT = ["500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r", "523.xalancbmk_r", "525.x264_r", "531.deepsjeng_r", "541.leela_r", "548.exchange2_r", "557.xz_r"]
    CFP = ["503.bwaves_r", "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r", "519.lbm_r", "521.wrf_r", "526.blender_r", "527.cam4_r", "538.imagick_r", "544.nab_r", "549.fotonik3d_r", "554.roms_r"]

    FP_NO_FORTRAN = [ "508.namd_r", "510.parest_r", "511.povray_r", "519.lbm_r", "526.blender_r", "538.imagick_r", "544.nab_r"]
    INT_NO_FORTRAN = [ "500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r", "523.xalancbmk_r", "525.x264_r", "531.deepsjeng_r", "541.leela_r", "557.xz_r"]

else:
    print(f"{SPEC} not exsited")
    exit(1)

# if "perf" in cmd_prefix or "pin" in cmd_prefix:
#     cmd = (cmd_prefix % ("/dev/null")) + " /bin/ls 1>/dev/null 2>/dev/null"
#     if os.system(cmd):
#         print("can not run prefix")
#         print(cmd)
#         exit(1)

if not os.path.exists(base_dir) :
    print(f"{base_dir} not existed")
    exit(1)

score_file = open(log_dir + ".csv", "w")

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
        cmd_args = line[:-1].split(" ")
        # print(cmd_args)
        i = 0
        stdin = ""
        stdout = ""
        stderr = ""
        while i < len(cmd_args) :
            if cmd_args[i] == "-i":
                stdin = cmd_args[i + 1]
                i += 1
            elif cmd_args[i] == "-o":
                stdout = cmd_args[i + 1]
                i += 1
            elif cmd_args[i] == "-e":
                stderr = cmd_args[i + 1]
                i += 1
            else :
                break
            i += 1
        cmd = " ".join(cmd_args[i:])
        if SPEC == "2017":
            for i in range(0, len(cmd)):
                # 2017 append < in > stdout 2>> stderr at end of command
                if cmd[i] in ['>', '<', '2>>'] :
                    cmd = cmd[:i]
                    break
        # print(stdin, stdout, stderr, cmd)
        if EXE_DIR :
            cmd_sp = cmd.strip().split()
            exepath = cmd_sp[0]
            basename = os.path.basename(exepath)
            benchname = basename[:basename.find("_")]
            if "_base" in basename:
                benchname = basename[:basename.find("_base")]
            elif "_peak" in basename:
                benchname = basename[:basename.find("_peak")]
            else:
                print(basename, "has not _base and _peak")
                exit(0)
            realpath_exe = glob.glob(os.path.join(EXE_DIR, benchname + "*"))[0]
            if args.copy_exe:
                shutil.copy2(realpath_exe, os.path.dirname(speccmds_filename))
                cmd = " ".join(["./" + os.path.basename(realpath_exe)] + cmd_sp[1:])
            else:
                cmd = " ".join([realpath_exe] + cmd_sp[1:])
        if args.dup_exe:
            cmd = cmd.strip().split()[0] + " " + cmd
        # print(cmd)
        intfp = ""
        if args.intfp:
            intfp = "int_" if benchmark in CINT else "xfp_"
        logfile = log_dir + "/" + intfp + benchmark + "_" + str(index) + args.suffix
        if "%s" in cmd_prefix:
            cmd_full_prefix = cmd_prefix.replace("%s", logfile)
        elif not cmd_prefix :
            cmd_full_prefix = ""
        else :
            cmd_full_prefix = cmd_prefix + " "
        if args.redirect_stderr:
            stderr = logfile + ".stderr"
        cmd = " ".join([cmd_full_prefix, cmd, ("<"+stdin) if stdin else "", ("1>" +stdout) if stdout else "", ("2>" + stderr) if stderr else ""])
        cmds.append(cmd)
    # print(cmds)
    return cmds

def run_single(benchmark, get_cmd_only=False):
    DIR_PREFIX = ""
    if SPEC == "2000" :
        DIR_PREFIX = 'CINT2000' if benchmark in CINT else 'CFP2000'
    work_dir = os.path.join(base_dir, DIR_PREFIX,  benchmark, sub_dir)
    if not os.path.exists(work_dir):
        print(f"{work_dir} not existed")
        exit(1)
    cmds = get_command(benchmark, os.path.join(work_dir, "speccmds.cmd"))
    if get_cmd_only :
        return ["cd %s && %s" % (work_dir, cmd) for cmd in cmds]

    reftime = get_reftime(os.path.join(base_dir, DIR_PREFIX, benchmark, "data/%s/reftime" % (SIZE)), benchmark)
    os.chdir(work_dir)
    begin = time.time()
    for cmd in cmds:
        if dry_run or verbose:
            print("cd %s && %s" % (work_dir, cmd))

        if not dry_run:
            r = os.system(cmd)
            if r:
                print("error %s, return value:%d" % (benchmark, r))
                print("work_dir %s" % (work_dir))
                print("cmd %s" % (cmd))
                if not ignore_error :
                    exit(r)
    end = time.time()
    runtime = end - begin
    return reftime, runtime, reftime / runtime

def cd_exec(work_dir, cmd):
    os.chdir(work_dir)
    return os.system(cmd)

def RUN(benchmarks):
    scores = []
    for benchmark in benchmarks:
        reftime, runtime, ratio = run_single(benchmark)
        if not dry_run:
            print("%20s\t%.1f\t%.3f\t%.3f" % (benchmark, reftime, runtime, ratio))
            score_file.write('%s,%f,%f,%f\n' % (benchmark, reftime, runtime, ratio))
        scores.append(ratio)
    if not dry_run:
        geo_mean = reduce(lambda x, y: x*y, scores)**(1.0/len(scores))
        print("score : %.3f" % geo_mean)
        score_file.write("score,,,%s\n" % geo_mean)


# def RUN_MT(benchmarks):
#     scores = []
#     with Pool(THREADS) as p:
#         r = p.map(run_single, benchmarks)
#         for index in range(len(benchmarks)):
#             reftime, runtime, ratio = r[index]
#             if not dry_run:
#                 print("%20s\t%.1f\t%.3f\t%.3f" % (benchmarks[index], reftime, runtime, ratio))
#             scores.append(ratio)
#     if not dry_run:
#         print("score : %.3f" % reduce(lambda x, y: x*y, scores)**(1.0/len(scores)))

# def RUN_MT2(benchmarks):
#     cmds = []
#     for i in benchmarks:
#         cmds += run_single(i, True)
#     with Pool(THREADS) as p:
#         r = p.map(os.system, cmds)
#         for index in range(len(cmds)):
#             print("FAIL:", end='') if r[index] else print("SUCCESS:", end='')
#             print(cmds[index].split("&&")[1])

def RUN_MT3(benchmarks):
    cmds = []
    for i in benchmarks:
        cmds += run_single(i, True)
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        h264_1_2017 = "--pass 1 --stats x264_stats.log --bitrate 1000 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"
        h264_2_2017 = "--pass 2 --stats x264_stats.log --bitrate 1000 --dumpyuv 200 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"
        cmdsA = [_ for _ in cmds if h264_2_2017 not in _]
        cmdsB = [_ for _ in cmds if h264_2_2017 in _]
        if cmdsB :
            cmdsB = cmdsB[0]
            print("detected h264_2_2017")
        futures = {
            executor.submit(os.system, task): task for task in cmdsA
        }

        while futures:
            done_future = next(as_completed(futures))
            task_name = futures.pop(done_future)

            try:
                print(task_name)
                result = done_future.result()
                if result :
                    print(f"FAIL:{task_name}")
                else:
                    print(f"SUCCESS:{task_name}")

                if h264_1_2017 in task_name and not result:
                    b2_future = executor.submit(os.system, h264_2_2017)
                    futures[b2_future] = h264_2_2017
                    print("2017 : Submitted h264_2 after h264_1")

            except Exception as e:
                print(f"Task {task_name} failed: {str(e)}")

if not dry_run:
    print("begin : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

def canonical_list(raw_name, canonical_name):
    r = []
    for raw in raw_name:
        for item in canonical_name:
            if raw in item:
                r.append(item)
    return r

benchmark = args.benchmark.split(",")
b_int = canonical_list(benchmark, CINT)
b_fp = canonical_list(benchmark, CFP)

if THREADS == 1:
    if "int" in benchmark or "all" in benchmark:
        RUN(CINT)
    if "fp" in benchmark or "all" in benchmark:
        RUN(CFP)
    if b_int:
        RUN(b_int)
    if b_fp:
        RUN(b_fp)
else:
    if "int" in benchmark:
        RUN_MT3(CINT)
    if "fp" in benchmark:
        RUN_MT3(CFP)
    if "all" in benchmark:
        RUN_MT3(CINT + CFP)
    if "fp_no_fortran" in benchmark:
        RUN_MT3(FP_NO_FORTRAN)
    if "int_no_fortran" in benchmark:
        RUN_MT3(INT_NO_FORTRAN)
    if "no_fortran" in benchmark:
        RUN_MT3(FP_NO_FORTRAN + INT_NO_FORTRAN)

if not dry_run:
    print("end   : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

score_file.close()
