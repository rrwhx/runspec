#!/bin/bash
# Source: https://github.com/rrwhx/runspec

# 检查参数是否正确
if [ $# -eq 0 ]; then
    echo "Usage: $0 <suffix|all> [suffix2] [suffix3] ..."
    exit 1
fi

# 启用nullglob以避免无匹配时字面量扩展
shopt -s nullglob

# 如果第一个参数是all，则获取所有suffix
if [ "$1" = "all" ]; then
    suffix_list=( $(ls benchspec/*/*/exe/ | grep -E "_((base)|(peak)).*" -o | sort | uniq) )
else
    # 否则使用传入的所有参数作为suffix列表
    suffix_list=("$@")
fi

echo ${suffix_list[@]}

# 所有 exe 目录统一收纳到该上层输出目录下
output_root="./exes"
mkdir -p "$output_root"

# 遍历所有suffix
for suffix in "${suffix_list[@]}"; do
    # 目录名去掉前导下划线（base/peak 开头），但匹配仍用完整 suffix
    # 在 output_root 下再建一层，各个 exe 目录归于其中
    target_dir="${output_root}/${suffix#_}"

    # 创建目标目录
    mkdir -p "$target_dir"
    echo "Processing suffix: $suffix, target directory: $target_dir"

    # 遍历所有匹配的文件
    for file in benchspec/*/*/exe/*"$suffix"; do
        # 检查文件是否存在
        if [ -f "$file" ]; then
            echo "$file"
            cp "$file" "${target_dir}/"
        fi
    done
done

# 恢复nullglob
shopt -u nullglob

echo "处理完成"
