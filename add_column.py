#!/usr/bin/env python3
import sys
import re
import argparse

def parse_csv_line(line):
    """
    简单的CSV行解析，处理逗号分隔和引号包围的字段
    """
    fields = []
    current_field = ""
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]

        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                # 转义的引号
                current_field += '"'
                i += 1
            else:
                # 切换引号状态
                in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            # 字段分隔符
            fields.append(current_field.strip())
            current_field = ""
        else:
            current_field += char

        i += 1

    # 添加最后一个字段
    fields.append(current_field.strip())
    return fields

def format_csv_field(field):
    """
    格式化CSV字段，如果包含逗号、引号或换行符则用引号包围
    """
    field_str = str(field)
    if ',' in field_str or '"' in field_str or '\n' in field_str:
        # 转义引号并用引号包围
        escaped = field_str.replace('"', '""')
        return f'"{escaped}"'
    return field_str

def safe_eval(expression, variables):
    """
    安全地评估表达式，只允许基本的数学运算和比较
    """
    # 允许的操作符和函数
    allowed_names = {
        '__builtins__': {},
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'int': int,
        'float': float,
        'str': str,
        'len': len,
    }

    # 添加变量
    allowed_names.update(variables)

    try:
        # 使用eval但限制可用的名称空间
        result = eval(expression, allowed_names, {})
        return result
    except Exception as e:
        print(f"表达式计算错误: {e}", file=sys.stderr)
        return ""

def convert_to_number(value):
    """
    尝试将字符串转换为数字，失败则返回原字符串
    """
    if isinstance(value, (int, float)):
        return value

    value_str = str(value).strip()
    if not value_str:
        return 0

    try:
        # 尝试转换为整数
        if '.' not in value_str:
            return int(value_str)
        else:
            return float(value_str)
    except ValueError:
        return value_str

def process_csv(input_file, expression, column_name=None, output_file=None, verbose=False):
    """
    处理CSV文件，添加新列
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"读取文件错误: {e}", file=sys.stderr)
        return False

    if not lines:
        print("文件为空", file=sys.stderr)
        return False

    # 准备输出流
    output_stream = sys.stdout
    if output_file:
        try:
            output_stream = open(output_file, 'w', encoding='utf-8')
        except Exception as e:
            print(f"创建输出文件错误: {e}", file=sys.stderr)
            return False

    try:
        # 处理第一行
        first_line = lines[0].strip()
        first_row = parse_csv_line(first_line)

        has_header = column_name is not None
        start_row = 1 if has_header else 0

        # 输出header（如果有）
        if has_header:
            output_row = first_row + [column_name]
            print(','.join(format_csv_field(field) for field in output_row), file=output_stream)

        # 处理数据行
        processed_rows = 0
        for line_num, line in enumerate(lines[start_row:], start=start_row + 1):
            line = line.strip()
            if not line:
                continue

            row = parse_csv_line(line)

            # 准备变量字典，支持负数索引
            variables = {}
            for i, value in enumerate(row):
                # 尝试转换为数字
                converted_value = convert_to_number(value)
                variables[f'c{i}'] = converted_value
                # 支持负数索引
                variables[f'c{i - len(row)}'] = converted_value

            # 计算新列的值
            try:
                new_value = safe_eval(expression, variables)
            except Exception as e:
                if verbose:
                    print(f"第 {line_num} 行计算错误: {e}", file=sys.stderr)
                new_value = ""

            # 输出行
            output_row = row + [new_value]
            print(','.join(format_csv_field(field) for field in output_row), file=output_stream)
            processed_rows += 1

        if verbose:
            print(f"成功处理 {processed_rows} 行数据", file=sys.stderr)

        return True

    finally:
        # 关闭输出文件（如果有）
        if output_file and output_stream != sys.stdout:
            output_stream.close()

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='为CSV文件添加基于表达式计算的新列',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:

1. 基本数学运算（第一行作为数据）:
   python add_column.py data.csv "c0 + c1"
   # 将第0列和第1列相加，结果作为新列

2. 指定新列名（第一行作为header）:
   python add_column.py data.csv "c1 + c2" --column-name "总分"
   # 将第1列和第2列相加，新列名为"总分"

3. 复杂数学表达式:
   python add_column.py sales.csv "c1 * 0.1 + c2 * 0.05" --column-name "佣金"
   # 计算佣金：销售额*10% + 奖金*5%

4. 条件表达式:
   python add_column.py grades.csv "c1 if c1 >= 60 else 0" --column-name "及格分数"
   # 如果分数>=60则保持原分数，否则为0

5. 使用内置函数:
   python add_column.py data.csv "max(c0, c1, c2)" --column-name "最大值"
   # 取前三列的最大值

6. 字符串长度计算:
   python add_column.py names.csv "len(str(c0))" --column-name "姓名长度"
   # 计算第0列字符串的长度

7. 四舍五入:
   python add_column.py prices.csv "round(c0 * 1.13, 2)" --column-name "含税价格"
   # 计算含税价格并保留2位小数

8. 多条件判断:
   python add_column.py scores.csv "('优秀' if c0 >= 90 else '良好' if c0 >= 80 else '及格' if c0 >= 60 else '不及格')" --column-name "等级"
   # 根据分数划分等级

9. 就地编辑（直接修改源文件）:
   python add_column.py data.csv "c0 * 1.1" --column-name "调整后价格" --in-place
   # 直接修改源文件，添加新列

10. 输出到指定文件:
    python add_column.py input.csv "c1 + c2" --column-name "总计" --output output.csv
    # 将结果保存到新文件

列引用说明:
- c0, c1, c2... 分别代表CSV文件的第0列、第1列、第2列...
- 支持负数索引，如 c-1 代表最后一列
- 数字列会自动转换为数值类型进行计算
- 非数字列保持字符串类型

支持的函数和操作:
- 数学运算: +, -, *, /, //, %, **
- 比较运算: ==, !=, <, <=, >, >=
- 逻辑运算: and, or, not
- 内置函数: abs(), min(), max(), round(), int(), float(), str(), len()
- 条件表达式: value if condition else other_value
        '''
    )

    parser.add_argument('input_file',
                       help='输入的CSV文件路径')

    parser.add_argument('expression',
                       help='计算表达式，使用 c0, c1, c2... 引用列')

    parser.add_argument('-c', '--column-name',
                       help='新增列的名称。如果指定，第一行将被视为header；否则第一行视为数据')

    parser.add_argument('-v', '--verbose',
                       action='store_true',
                       help='显示详细的处理信息')

    parser.add_argument('-o', '--output',
                       help='输出文件路径（默认输出到标准输出）')

    parser.add_argument('-i', '--in-place',
                       action='store_true',
                       help='直接修改源文件（就地编辑）')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # 检查参数冲突
    if args.in_place and args.output:
        print("错误: 不能同时使用 -i (就地编辑) 和 -o (输出文件) 选项", file=sys.stderr)
        sys.exit(1)

    # 如果使用就地编辑，设置输出文件为输入文件
    output_file = args.input_file if args.in_place else args.output

    # 验证表达式中的列引用
    column_refs = re.findall(r'c-?\d+', args.expression)
    if not column_refs and args.verbose:
        print("警告: 表达式中没有找到列引用 (c0, c1, c2, ...)", file=sys.stderr)

    if args.verbose:
        print(f"处理文件: {args.input_file}", file=sys.stderr)
        print(f"表达式: {args.expression}", file=sys.stderr)
        if args.column_name:
            print(f"新列名: {args.column_name}", file=sys.stderr)
            print("第一行视为header", file=sys.stderr)
        else:
            print("第一行视为数据", file=sys.stderr)
        if args.in_place:
            print("就地编辑模式：直接修改源文件", file=sys.stderr)
        elif args.output:
            print(f"输出到文件: {args.output}", file=sys.stderr)

    success = process_csv(args.input_file, args.expression, args.column_name, output_file, args.verbose)

    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
