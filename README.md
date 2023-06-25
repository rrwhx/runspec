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
- spec cpu2000
```bash
rm -rf benchspec/*/*/run/
runspec -c x64.cfg -i test  -n 1 all
runspec -c x64.cfg -i train -n 1 all
runspec -c x64.cfg -i ref   -n 1 all
```
保证 run 目录下生成`00000001  00000002  00000003`分别对应`test train ref`

- spec cpu2006
```bash
rm -rf benchspec/CPU2006/*/run/
runspec -c x64.cfg -i test  -n 1 all -a setup
runspec -c x64.cfg -i train -n 1 all -a setup
runspec -c x64.cfg -i ref   -n 1 all -a setup
```

- spec cpu2017
```bash
rm -rf benchspec/CPU/*/run/
runspec -c x64.cfg -i test  -n 1 -a setup intrate fprate
runspec -c x64.cfg -i train -n 1 -a setup intrate fprate
runspec -c x64.cfg -i ref   -n 1 -a setup intrate fprate
```

## 使用

```bash
usage: runspec.py [-h] [-i {test,train,ref,refrate}] [-b BENCHMARK] [-T {base,peak}] [--ext EXT] [-t THREADS] [-l] [-n] [-v] [-c CMD_PREFIX] [--title TITLE] [--stamp STAMP]
                  [--result_dir RESULT_DIR] [--dir DIR] [--slimit SLIMIT]

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
  -t THREADS, --threads THREADS
                        Allow N jobs at once;
  -l, --loose           ignore errors
  -n, --dry_run         Don't actually run any cmd; just print them.
  -v, --verbose         Print cmd before exec cmd
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
./runspec.py -i ref -s 2006 -b all -t 4 \
    --dir06 /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/ \
    --ext06 Ofast_static_x64 -c "/usr/bin/time -f %%M -o %s " \
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



