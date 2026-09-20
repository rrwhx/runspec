#!/usr/bin/env bash
# Source: https://github.com/rrwhx/runspec

# 检查参数数量（至少 1 个参数）
if [ $# -lt 1 ]; then
    echo "Usage: $0 <suffix> [objdump_command] [args...]"
    exit 1
fi

suffix="$1"
# 使用环境变量 TARGET_DIR 指定输出目录，默认值为 ./${suffix}_asm
target_dir="${TARGET_DIR:-./${suffix}_asm}"
shift 1

# 如果提供了后续参数，则将其作为 objdump 命令
if [ $# -ge 1 ]; then
    objdump_cmd=( "$@" )
else
    # 否则尝试查找可用的 objdump 命令
    if command -v llvm-objdump &> /dev/null; then
        objdump_cmd=("llvm-objdump")
    elif command -v objdump &> /dev/null; then
        objdump_cmd=("objdump")
    else
        echo "Error: Neither 'llvm-objdump' nor 'objdump' is available in PATH."
        exit 1
    fi
fi

# 检查指定的 objdump 命令是否可执行
if ! command -v "${objdump_cmd[0]}" &> /dev/null; then
    echo "Error: Command '${objdump_cmd[*]}' not found or not executable."
    exit 1
fi

echo "Using objdump command: ${objdump_cmd[*]}"

# 创建目标目录
mkdir -p "$target_dir"

# 启用 nullglob 以避免无匹配时字面量扩展
shopt -s nullglob

# 初始化匹配计数器
matched=0

# 遍历所有匹配的文件
for file in benchspec/*/*/exe/*."$suffix"; do
    # 提取基础文件名（去除后缀）
    base_name=$(basename "$file" ".$suffix")
    # 反汇编并输出到目标文件
    echo "Processing: $file"
    "${objdump_cmd[@]}" -d "$file" > "${target_dir}/${base_name}"
    ((matched++))
done

# 恢复 nullglob
shopt -u nullglob

# 检查是否匹配到任何文件
if [ $matched -eq 0 ]; then
    echo "Error: No files matched pattern 'benchspec/*/*/exe/*.$suffix'"
    exit 1
fi

echo "Successfully processed $matched file(s)."
echo "Output directory: $target_dir"
