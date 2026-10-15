# runspec
Source: https://github.com/rrwhx/runspec

用于收集任何spec cpu(2000/2006/2017)的数据

## 简介
基于python的脚本，替代spec官方的runspec脚本，可以运行在spec的命令前加上各种前缀命令,
与config中的submit和use_submit_for_speed参数比较相似。

## 安装

` git clone https://github.com/rrwhx/runspec `

## 仓库结构

```
runspec/
├── runspec.py          # 核心:在 SPEC 命令前加前缀运行,收集日志/性能数据
├── run.sh              # SPEC 目录内的运行/构建入口(需 cp 到 spec_root)
├── templates/          # 各版本/负载的静态命令脚本(生成物,非手写逻辑)
│   └── cpu2000_*.sh, cpu2006_*.sh, cpu2017_*_rate.sh, cpu2026_*_rate.sh
├── env/                # 环境准备与维护
│   ├── setup_spec.sh       # 建立 test/train/ref run 目录
│   ├── clean_spec.sh       # 清理 run 目录
│   ├── copy_exe.sh         # 导出各 bench 的可执行文件
│   └── rename_int_fp.sh    # int_/xfp_ 前缀重命名
├── collect_perf.py       # perf stat 输出 → CSV
├── collect_score.py      # SPEC 结果 log → score CSV(含 GMEAN)
├── collect_disassemble.sh  # 批量 objdump benchspec 下的可执行文件
├── collect_disassemble.py  # 反汇编辅助(交叉工具链)
├── csv_merge.py          # 水平/纵向拼接多个 CSV
├── csv_combine.py        # 选取列并排合并
├── csv_add_column.py     # 按表达式添加派生列
├── csv_reduce.py         # 按 benchmark/分组聚合(sum/mean/geomean 等)
├── csv_eval.py           # 按表达式计算列
├── csv_query.py          # 筛选、分组、聚合、排序
├── csv_pivot.py          # 长表转宽表
├── csv_extract_columns.py # 按列名/列号提取或排除列
├── csv_sample.py         # 多文件随机/均匀抽样并合并
├── csv_split_by_column.py # 按一列或多列的值拆分文件
├── csv_add_random.py     # 给数值列添加随机扰动
├── _csv_common.py        # 所有 CSV 工具的格式、校验与文件读写
├── requirements-csv.txt  # CSV 分析工具的可选依赖
├── ruff.toml             # CSV 工具的统一格式与静态检查配置
└── tests/test_csv_tools.py # CSV 工具命令行回归测试
```

约定:
- 采集/处理类脚本均为 数据 → stdout,日志/警告 → stderr,可用管道直接串联。
- 新脚本按职能命名:采集用 `collect_` 前缀,CSV 处理用 `csv_` 前缀,生成物入 `templates/`,环境脚本入 `env/`。

## CSV 数据处理

全部 11 个 `csv_*.py` 工具共用同目录的 `_csv_common.py`，复制到其他位置时需一起复制。
脚本使用统一的命令行入口、格式参数和错误处理；导入模块不会触发命令行解析或处理数据。

| 工具 | 用途 |
| --- | --- |
| `csv_add_column.py` | 按 `c0`、`c1` 或 `c[index]` 逐行计算一个新列，支持原地更新 |
| `csv_eval.py` | 按列名计算多个表达式，支持数学函数和显式类型转换 |
| `csv_extract_columns.py` | 按列名、列号或范围提取、排除列 |
| `csv_combine.py` | 从多个文件选取列，按行位置并排组合 |
| `csv_merge.py` | 横向或纵向合并，可保留所有键/表头、按键去重 |
| `csv_query.py` | 筛选、分组聚合、排序、截取行 |
| `csv_reduce.py` | 数值汇总，含几何/调和平均；兼容 SPEC 两级汇总，也支持精确键 |
| `csv_pivot.py` | 长表转宽表，显式选择聚合和空值处理 |
| `csv_sample.py` | 对多个文件抽样并合并，保留字段文本和行顺序 |
| `csv_split_by_column.py` | 按一列或多列拆分，处理文件名冲突 |
| `csv_add_random.py` | 为指定数值列添加可复现的随机扰动 |

### 依赖与输入输出

使用 Python 3.9 或更高版本。仅 `csv_eval.py`、`csv_query.py`、`csv_pivot.py`
和 `csv_add_random.py` 需要 pandas / NumPy，其他工具仅使用标准库：

```bash
python3 -m pip install -r requirements-csv.txt
```

所有工具统一使用以下约定：

- 输入文件使用位置参数，单输入工具省略文件或指定 `-` 时读取 stdin。
  合并与抽样不传文件时也读取 stdin；组合工具使用 `- INDEX ...` 选择标准输入的列。
  随机扰动工具也保留 `-i` 输入别名。
- `-d` 指定输入分隔符，`-t` 读取 TSV；`--output-delimiter` 指定输出分隔符，默认逗号。
- `--encoding` 指定输入编码，默认 UTF-8 并自动识别 BOM；`--output-encoding` 默认 UTF-8。
- 除拆分工具外，`-o` 指定输出文件，省略或为 `-` 时写入 stdout；错误写入 stderr 并返回非零状态。
- 输出文件先写临时文件，成功后替换目标文件；拆分工具在全部输入处理成功后才发布各个分组文件。
- 列号从 **0** 开始。大部分工具默认输入含表头；提取、抽样和拆分支持 `-H` 读取无表头数据。
  `csv_add_column.py` 仅在指定 `-c` 时把首行当作表头；`csv_combine.py` 默认把所有输入行当作数据，
  `--skip-header` 跳过输入表头，`--no-header` 关闭自动生成的输出表头。

提取、抽样、拆分会保留字段文本，随机扰动只转换选中的数值列。
表达式、查询、透视会推断数据类型；需要保留 `001` 等编号时使用 `--string-columns id,zip`。
分析工具仅把空字段视为缺失值，`NA`、`null` 等文本不会自动转为空值。
表达式、查询、透视和随机扰动在类型推断前校验列数和重复列名，避免静默丢列或重命名。

### 常用操作

以下示例假设 `sales.csv` 含 `product,region,price,quantity` 列。

```bash
# 按表达式计算金额
python3 csv_eval.py sales.csv -e 'amount=price*quantity' -o derived.csv

# 逐行按列号计算；c[-1] 表示最后一列
python3 csv_add_column.py sales.csv 'c2 * c[-1]' -c amount -o derived.csv

# 横向合并共享首列键的文件；纵向合并用 -v
python3 csv_merge.py prices.csv quantities.csv -o combined.csv
python3 csv_merge.py -v january.csv february.csv -o all_sales.csv

# 各文件的第 1、2 列并排组合，跳过输入表头
python3 csv_combine.py --skip-header january.csv february.csv 1 2 -o selected_columns.csv

# 按完整产品名计算几何平均价格，不生成 SPEC 分组汇总
python3 csv_reduce.py sales.csv --key product --key-mode exact -e price -r geometric --no-group-summary

# 筛选、按地区聚合，再按金额降序排列
python3 csv_query.py derived.csv -f 'quantity > 0' -g region -a amount:sum -s amount:desc

# 产品为行、地区为列，重复键按金额求和
python3 csv_pivot.py derived.csv -i product -c region -v amount -a sum

# 提取列；也可用 -c '0,2-3' 按列号选择，或用 -C 排除列
python3 csv_extract_columns.py sales.csv -c product,price,quantity

# 每个文件随机抽样 10%，固定种子；-n 100 优先于采样率，-m uniform 改用均匀抽样
python3 csv_sample.py data/ -r 0.1 --seed 42 -o sampled.csv

# 按地区拆分，生成 parts/sales_<region>.csv；--prefix 可指定文件名前缀
python3 csv_split_by_column.py sales.csv -c region -o parts

# 数值列添加可复现的均匀扰动
python3 csv_add_random.py sales.csv -c price -r -0.5 0.5 --seed 42 -o noisy.csv

# 管道串联：计算 → 筛选 → 提取列
python3 csv_eval.py sales.csv -e 'amount=price*quantity' \
  | python3 csv_query.py -f 'amount > 100' \
  | python3 csv_extract_columns.py -c product,region,amount > selected.csv
```

### 行为与兼容性变化

- **按列号计算**：支持正确的引号、多行字段和科学计数法；负列号使用 `c[-1]`，
  不使用有歧义的 `c-1`。空字符串不再隐式转成 0，计算错误默认报错，
  `--on-error empty` 可显式输出空值。`-i/--in-place` 成功后才替换原文件。
- **组合**：保留 `FILE [FILE ...] INDEX [INDEX ...]` 参数形式及负列号。
  空文件和较短文件也会为所选列保留位置；缺失字段默认补空，可用 `--missing error` 改为报错。
- **合并**：仍默认共享第一列（横向）或第一行（纵向），`-k` 保留所有列/行。
  现在默认校验横向的逐行键、纵向的表头；需要按位置强行拼接时显式指定 `--by-position`。
  这是位置拼接，不会按键重排或执行 join。`-u` 横向按表头去重列、纵向按首列去重数据行，
  保留首次出现项，空键不参与去重。首个文件为空时使用后续第一个非空文件的键/表头。
- **数值汇总**：默认写 stdout，不再自动创建 `result.csv`；需要文件时指定 `-o result.csv`。
  `--key-mode spec`（默认）仅剥离末尾 `_数字`，保留名称中的其他下划线；
  `--key-mode exact` 按完整键分组。默认按 `int_`、`xfp_` 或首个 `-` 前缀生成组汇总，
  无前缀的键归入 `all`；`--no-group-summary` 或 `-r2 none` 可关闭第二级汇总。
  `-e` 现在实际选择数值列，默认选择键以外的全部列。输出保留完整键名，不再删除组前缀，
  避免同名记录互相覆盖。无效数值、结果溢出或汇总名称冲突会报错。
- **表达式计算**：按顺序执行，可引用前面创建的列；含空格或连字符的列名使用反引号。
  `diff(value)` 保留首行和原始缺失值；需要补零时显式写 `diff(value).fillna(0)`。
  默认保留正负无穷，可用 `--non-finite empty` 转为空值或 `--non-finite error` 报错。
- **移除旧流程快捷函数**：`dt_year/month/day/hour/minute/second/weekday`、`strftime`
  以及表达式中的 `random/uniform/normal/randint` 已移除。
  通用时间转换使用 `to_datetime(date).dt.hour` 或 `to_datetime(date).dt.strftime('%Y-%m-%d')`；
  随机扰动使用独立的 `csv_add_random.py`。
- **查询**：空分组键默认保留，`--drop-na-groups` 可丢弃；错误的排序列和排序方向会报错。
  单函数聚合保留列名，与分组列同名时加函数后缀；多函数聚合使用 `列名_函数`。
- **透视**：不指定 `-a` 时重复键报错；默认保留缺失数据，`--fill-value` 显式填充空单元格，
  `--drop-na` 丢弃有空值的结果行。不会按列名自动解析日期。
- **抽样**：按输入顺序处理文件，抽样后保持行顺序；每个文件的比例采样行数向下取整。
  `-n` 优先于 `-r`，两者都支持 0；默认扫描目录的 `*.csv`，可用 `--pattern '*.tsv' -t`。
  显式文件参数不限制扩展名；去重并排除已有输出文件。多文件表头和列数必须一致，
  不再自动取列名并集。完整复制为流式处理；随机 `-n N` 使用蓄水池抽样，只保留至多 N 行。
  比例抽样和均匀抽样仍需暂存单个输入文件。算法调整后相同种子的结果可能与旧版本不同，
  同一版本中相同输入与参数仍可复现。
- **拆分**：`-o` 现在始终是目录。原来的 `-o part_` 前缀写法改为 `-o . --prefix part_`。
  文件名清理后发生冲突会加数字后缀，支持长中文键；默认最多打开 64 个输出文件，
  可用 `--max-open-files` 调整。默认不再静默丢弃缺少分组字段的行，改为报错；
  `--missing skip` 显式跳过，`--missing group` 单独分组（兼容 `--keep-missing`）。
- **提取列**：短行默认报错，`--missing empty` 显式补空值。所有工具输出默认统一为逗号分隔，
  拆分 TSV 如需维持制表符，传入 `--output-delimiter $'\t'`。

### 验证

```bash
python3 -m unittest discover -s tests -v

# 可选开发工具：python3 -m pip install ruff
ruff check .
ruff format --check .
```

`ruff.toml` 将检查范围限定为 CSV 工具及其测试，统一导入排序、双引号和 100 字符行宽。
测试覆盖全部工具的入口、管道、编码、CSV 引号/多行、合并与汇总、抽样、拆分和失败回滚。

## 预先准备

编译好的spec cpu目录

### 建立run目录

### 方案 1

保证 run 目录下生成三个文件夹分别对应`test train ref`
```bash
cd <spec_root>
cp run.sh env/setup_spec.sh .
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

#### 收集每个子项使用的内存大小

```bash
./runspec.py -i ref -b all -t 4 \
    --dir /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/ \
    --cmd_prefix "/usr/bin/time -f %%M -o %s " \
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

#### 测量QEMU效率

```bash
./runspec.py -i ref -b int \
    --dir /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/ \
    --cmd_prefix "qemu-x86_64 -- " \
    --title qemu_log
```

#### 测试原生性能

```bash
./runspec.py -i ref -b int \
    --dir /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/
```

#### Perf record IPC

```bash
./runspec.py -i ref -b int \
    --dir /2t/SPEC/SPEC2006/lxy/spec2006_x64_avx2/ \
    --cmd_prefix "taskset -c 8 perf record -F 100 -e instructions -o %s --  " \
    --title perf_record_instructions
```

### FAQ:

#### `FAIL:***`？

命令执行失败，添加`-v`选项查看运行的目录和命令，手动运行查看原因。


