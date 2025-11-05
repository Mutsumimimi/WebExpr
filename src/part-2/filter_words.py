
import re
import sys
import os
    
# 常见的顶级域名 (TLD) 列表，如果 token 结尾是这些，则认为是网站，不分割。
# 这是一个不完全列表，您可以根据需要添加或删除。
COMMON_TLDS = {
    'com', 'cn', 'org', 'net', 'info', 'biz', 'co', 'io', 'gov', 
    'edu', 'pro', 'mobi', 'name', 'tech', 'xyz', 'top', 'site'
}
    
def filter_words(input_dirpath="output_data/"):
    """
    读取 input 文件，删除所有非“单词”的行，并将结果写入 *.flt
    
    “单词”的定义：只包含字母（a-z, A-Z）和数字（0-9），且非空。
    
    字母，数字，符号（包括连字符-_）
    只除去纯符号的行和纯数字的行
    剩下字母，字母+符号(hand-made)，字母+数字(1st)，字母+数字+符号(www.123.com)，符号+数字(6:30)
    """
    # word_pattern = re.compile(r"^[a-zA-Z0-9]+$")
    
    is_word = re.compile(r"^[a-zA-Z0-9]+$")
    digit_pattern = re.compile(r"^[0-9\W]+$")   # 改为去掉数字+符号
    symbol_pattern = re.compile(r"^[^\w\s]+$")
    dot_split_pattern = re.compile(r"^([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)$")
    single_pattern = re.compile(r"^[\w\S]$")

    for input_filename in os.listdir(input_dirpath):
        if input_filename.endswith('.conll'):
            # 用于存储符合条件的行
            lines_to_keep = []
            with open(f'{input_dirpath}{input_filename}', 'r', encoding='utf-8') as infile:
                for line in infile:
                    line = line.lower()
                    # 1. 清除行末的换行符和可能的空白字符，得到实际的“word”
                    stripped_line = line.strip() 
                    # 2. 检查清理后的行是否符合“单词”模式
                    if not stripped_line:
                        continue
                    # 检查是否是单词 is_word; 并删去 digit_pattern, symbol_pattern 类型的 token
                    if is_word.match(stripped_line) and not digit_pattern.match(stripped_line) and not symbol_pattern.match(stripped_line) and not single_pattern.match(stripped_line):
                        # 判断 token 是否需要是网站类型的
                        # 网站类型是 www.baidu.com, ustc.edu
                        # 非网站类型的通常是没有正确分割dot产生的，如
                        # interested.the history.september
                        match = dot_split_pattern.match(stripped_line)
                        if match:
                            # 捕获分割后的两部分
                            part1 = match.group(1)
                            part2 = match.group(2)
                            
                            if part2.lower() in COMMON_TLDS:
                                # 认为是“网站”，不分割，原样保留
                                lines_to_keep.append(line)
                            else:
                                # 认为是“非网站的 raw token，按点分割并加入结果列表
                                lines_to_keep.append(part1)
                                lines_to_keep.append(part2)
                        else:
                            # 保留原始行（包含换行符），以便写入文件时保持格式
                            lines_to_keep.append(line)
                            
                            
            '''
            input_filename 理想中是 *.desc.conll
            '''
            basename, externname = os.path.splitext(input_filename)
            basename, externname = os.path.splitext(basename)
            output_filename = f'{input_dirpath}{basename}.flt'
            # print(f"当前 basename 是{basename}\n")    
            
            # 写入 output.txt 文件
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.writelines(lines_to_keep)

            print(f"已将过滤后的内容写入 {output_filename}\n")  

        
filter_words(input_dirpath="output_data/")