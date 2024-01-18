# runspec
用于收集任何spec cpu(2000/2006/2017)的数据

## 简介
基于python的脚本，替代spec官方的runspec脚本，可以运行在spec的命令前加上各种前缀命令,
与config中的submit和use_submit_for_speed参数比较相似。

## 安装

` git clone https://github.com/rrwhx/runspec `

## 预先准备

编译好的spec cpu目录

### 建立run目录

### 方案 1

保证 run 目录下生成三个文件夹分别对应`test train ref`
```bash
cd <spec_root>
cp run.sh .
cp setup_spec.sh .
./run.sh <config_file> test 1 all
# cpu 2017
# ./run.sh <config_file> test 1 intrate fprate -T base
./setup_spec.sh <config_file>
```

### 方案 2

- spec cpu2000
保证 run 目录下生成`00000001  00000002  00000003`分别对应`test train ref`
```bash
# build
./run.sh <config_file> test 1 all
# setup run
rm -rf benchspec/*/*/run/
./run.sh <config_file> test  1 all
./run.sh <config_file> train 1 all
./run.sh <config_file> ref   1 all
```

- spec cpu2006
保证 run 目录下生成`run_base_test_<config_file>.0000 run_base_train_<config_file>.0000 run_base_ref_<config_file>.0000`分别对应`test train ref`
```bash
cd <spec_root>
# build
./run.sh <config_file> test 1 all
# setup run
rm -rf benchspec/CPU2006/*/run/
./run.sh <config_file> test  1 all -a setup
./run.sh <config_file> train 1 all -a setup
./run.sh <config_file> ref   1 all -a setup
```

- spec cpu2017
保证 run 目录下生成`run_base_test_<config_file>.0000 run_base_train_<config_file>.0000 run_base_refrate_<config_file>.0000`分别对应`test train ref`
```bash
source shrc
# build
./run.sh <config_file> test 1 intrate fprate -T base
# setup run
rm -rf benchspec/CPU/*/run/
./run.sh <config_file> test  1 -T base -a setup specrate
./run.sh <config_file> train 1 -T base -a setup specrate
./run.sh <config_file> ref   1 -T base -a setup specrate
```

## 使用

```bash
usage: runspec.py [-h] [-i {test,train,ref,refrate}] [-b BENCHMARK] [-T {base,peak}] [--ext EXT] [--suffix SUFFIX] [-t THREADS] [-l] [-n] [-v] [--intfp] [-c CMD_PREFIX] [--title TITLE]
                  [--stamp STAMP] [--result_dir RESULT_DIR] [--dir DIR] [--slimit SLIMIT]

Run spec cpu with prefix(none, qemu, perf, pin, dynamorio, strace, time), get log or performance,
Spec run directory should be prepared carefully,
Run test, train and ref in spec directory(00), or just -a setup(06,17), 

options:
  -h, --help            show this help message and exit
  -i {test,train,ref,refrate}, --size {test,train,ref,refrate}
  -b BENCHMARK, --benchmark BENCHMARK
                        benchmark selection, all/int/fp, comma separated items
  -T {base,peak}, --tune {base,peak}
  --ext EXT             auto probe, need not set
  --suffix SUFFIX       suffix of output file
  -t THREADS, --threads THREADS
                        Allow N jobs at once;
  -l, --loose           ignore errors
  -n, --dry_run         Don't actually run any cmd; just print them.
  -v, --verbose         Print cmd before exec cmd
  --intfp               intfp prefix
  -c CMD_PREFIX, --cmd_prefix CMD_PREFIX
                        cmd prefix before real cmd, %s for output, eg: -c "perf stat -o %s "
  --title TITLE
  --stamp STAMP
  --result_dir RESULT_DIR
                        location of cmd_prefix logs, defaults to ~/runspec_result
  --dir DIR
  --slimit SLIMIT       The limit of the stack size, 0 ulimited, or a number(MB), default: not modified
```

### 示例

```bash
./runspec.py -i ref -b all -t 4 \
    --dir /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/ \
    -c "/usr/bin/time -f %%M -o %s " \
    --title physical_memory_usage
```
```bash
cd ~/runspec_result/physical_memory_usage_2006_ref_2023_04_24_09_36_48/
grep -r . . | sort
./400.perlbench_1:242852
./400.perlbench_2:309456
./400.perlbench_3:679740
./401.bzip2_1:870216
./401.bzip2_2:102740
./401.bzip2_3:102760
./401.bzip2_4:870216
./401.bzip2_5:870208
./401.bzip2_6:625140
./403.gcc_1:237160
./403.gcc_2:257476
./403.gcc_3:454100
...
```

### FAQ:

#### `FAIL:***`？

命令执行失败，添加`-v`选项查看运行的目录和命令，手动运行查看原因。


