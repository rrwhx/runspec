#!/bin/bash

# 检查参数是否正确
if [ $# -ne 1 ]; then
    echo "Usage: $0 <suffix>"
    exit 1
fi

suffix="$1"
target_dir="./${suffix}"

# 创建目标目录
mkdir -p "$target_dir"

# 启用nullglob以避免无匹配时字面量扩展
shopt -s nullglob

# 遍历所有匹配的文件
for file in benchspec/*/*/exe/*."$suffix"; do
    # 提取基础文件名（去除后缀）
    base_name=$(basename "$file" ".$suffix")
    # 反汇编并输出到目标文件
    echo $file
    cp "$file" "${target_dir}/"
done

# 恢复nullglob
shopt -u nullglob

echo $target_dir



