#!/usr/bin/env python3
import sys
import csv

def usage():
    print("Usage:", file=sys.stderr)
    print("  python combine_csv2.py file1.csv file2.csv col1 col2 file3.csv col3 ...", file=sys.stderr)
    print("Example:", file=sys.stderr)
    print("  python combine_csv2.py file1.csv file2.csv 1 2 file3.csv 5", file=sys.stderr)
    print("Note: Column indices start from 0, support negative indices like Python", file=sys.stderr)

def parse_arguments(args):
    """
    解析命令行参数，返回文件名和对应的列索引列表
    格式: file1.csv file2.csv col1 col2 file3.csv col3 ...
    """
    if len(args) < 2:
        raise ValueError("至少需要一个文件和一个列索引")

    files_and_cols = []
    current_files = []
    current_cols = []

    i = 0
    while i < len(args):
        arg = args[i]

        # 尝试将参数解析为整数（列索引）
        try:
            col_index = int(arg)
            if not current_files:
                raise ValueError(f"列索引 {col_index} 前面没有指定文件")
            current_cols.append(col_index)
        except ValueError:
            # 不是整数，应该是文件名
            if current_files and current_cols:
                # 保存之前的文件和列索引组合
                files_and_cols.append((current_files.copy(), current_cols.copy()))
                current_files.clear()
                current_cols.clear()
            current_files.append(arg)

        i += 1

    # 处理最后一组
    if current_files and current_cols:
        files_and_cols.append((current_files.copy(), current_cols.copy()))
    elif current_files and not current_cols:
        raise ValueError(f"文件 {current_files} 后面没有指定列索引")

    return files_and_cols

def read_csv_columns(filename, col_indices):
    """
    从CSV文件中读取指定列的数据
    支持负数索引
    """
    print(f"正在处理文件: {filename}, 提取列: {col_indices}", file=sys.stderr)

    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
    except Exception as e:
        print(f"读取文件 {filename} 时出错: {e}", file=sys.stderr)
        raise

    if not rows:
        print(f"警告: 文件 {filename} 为空", file=sys.stderr)
        return []

    extracted_data = []
    for row_idx, row in enumerate(rows):
        extracted_row = []
        for col_idx in col_indices:
            try:
                # 支持负数索引
                if col_idx < 0:
                    actual_col = len(row) + col_idx
                else:
                    actual_col = col_idx

                if 0 <= actual_col < len(row):
                    extracted_row.append(row[actual_col])
                else:
                    print(f"警告: 文件 {filename} 第 {row_idx + 1} 行没有第 {col_idx} 列", file=sys.stderr)
                    extracted_row.append('')
            except Exception as e:
                print(f"警告: 处理文件 {filename} 第 {row_idx + 1} 行第 {col_idx} 列时出错: {e}", file=sys.stderr)
                extracted_row.append('')
        extracted_data.append(extracted_row)

    print(f"从文件 {filename} 提取了 {len(extracted_data)} 行数据", file=sys.stderr)
    return extracted_data

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    try:
        # 解析命令行参数
        files_and_cols = parse_arguments(sys.argv[1:])
        print(f"解析到 {len(files_and_cols)} 个文件组", file=sys.stderr)

        # 存储所有提取的数据
        all_extracted_data = []
        max_rows = 0

        # 处理每个文件组
        for files, cols in files_and_cols:
            for filename in files:
                extracted_data = read_csv_columns(filename, cols)
                all_extracted_data.append(extracted_data)
                if extracted_data:
                    max_rows = max(max_rows, len(extracted_data))

        print(f"最大行数: {max_rows}", file=sys.stderr)

        # 合并所有数据
        print("开始合并数据...", file=sys.stderr)
        writer = csv.writer(sys.stdout)

        for row_idx in range(max_rows):
            combined_row = []
            for data in all_extracted_data:
                if row_idx < len(data):
                    combined_row.extend(data[row_idx])
                else:
                    # 如果某个文件的行数不足，用空字符串填充
                    num_cols = len(data[0]) if data else 0
                    combined_row.extend([''] * num_cols)
            writer.writerow(combined_row)

        print(f"成功输出 {max_rows} 行合并数据", file=sys.stderr)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
