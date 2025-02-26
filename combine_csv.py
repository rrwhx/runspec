#!/usr/bin/env python3
import sys
import csv

def usage():
    print("Usage:")
    print("  python combine_csv.py input1.csv,col1,col2 ... inputN.csv,colX,... output.csv")
    print("Example:")
    print("  python combine_csv.py filename1.csv,1,2 filename2.csv,2 filename.csv,2 output.csv")

def parse_input_arg(arg):
    """
    解析形如 "文件名,列号1,列号2,..." 的参数，
    将文件名和列号（转换为 0 索引）返回
    """
    parts = arg.split(',')
    if len(parts) < 2:
        raise ValueError(f"参数格式错误: {arg}")
    filename = parts[0]
    try:
        # 将列号从 1 起的索引转换为从 0 起的索引
        col_indices = [int(x) - 1 for x in parts[1:]]
    except ValueError:
        raise ValueError(f"列号必须为整数: {arg}")
    return filename, col_indices

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    
    # 最后一个参数为输出文件名，其余参数为输入文件及待提取列信息
    out_filename = sys.argv[-1]
    input_args = sys.argv[1:-1]
    
    # 用来保存每个文件提取后的数据（二维列表）
    input_data_list = []
    # 用来记录每个文件有多少行
    num_rows_list = []
    
    # 循环处理每个输入文件
    for arg in input_args:
        try:
            filename, col_indices = parse_input_arg(arg)
        except ValueError as e:
            print(e)
            usage()
            sys.exit(1)
        
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
        except Exception as e:
            print(f"读取文件 {filename} 时出错: {e}")
            sys.exit(1)
        
        extracted_rows = []
        for row in rows:
            # 对于每一行，根据给定的列号提取相应列数据，如果超出范围则填空字符串
            extracted = []
            for col in col_indices:
                if col < len(row):
                    extracted.append(row[col])
                else:
                    extracted.append('')
            extracted_rows.append(extracted)
        
        input_data_list.append(extracted_rows)
        num_rows_list.append(len(extracted_rows))
    
    # 取所有文件中最大的行数，如果某个文件的行数不足，则对于该文件用空字符串补齐
    max_rows = max(num_rows_list) if num_rows_list else 0
    combined_rows = []
    
    for i in range(max_rows):
        combined_row = []
        for data in input_data_list:
            if i < len(data):
                combined_row.extend(data[i])
            else:
                # 当前文件该行不存在，补充对应数量的空字符串
                # 注意：这里假设每个文件至少有一行，否则会出错
                num_cols = len(data[0]) if data else 0
                combined_row.extend([''] * num_cols)
        combined_rows.append(combined_row)
    
    # 写入输出 CSV 文件
    try:
        with open(out_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(combined_rows)
    except Exception as e:
        print(f"写入输出文件 {out_filename} 时出错: {e}")
        sys.exit(1)
    
    print(f"成功生成输出文件：{out_filename}")

if __name__ == '__main__':
    main()
