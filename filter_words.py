#!/usr/bin/python3
import re
import sys
import os
# def filter_words(input_filename="test.txt.conll", output_filename="output.txt"):
#     """
#     读取 input.txt 文件，删除所有非“单词”的行，并将结果写入 output.txt。
    
#     “单词”的定义：只包含字母（a-z, A-Z）和数字（0-9），且非空。
#     """
    
#     # 正则表达式解释:
#     # ^       : 匹配行首
#     # \w+     : 匹配一个或多个单词字符 (字母、数字、下划线)
#     #           - 因为题目要求是单词、数字，所以我们只使用字母和数字的范围更准确。
#     #           - [a-zA-Z0-9]+: 匹配一个或多个字母或数字
#     # $       : 匹配行尾
#     # re.I    : 忽略大小写 (可选，但通常在处理“单词”时会使用)
#     #
#     # 为了更精确地符合“单词、数字”的要求，我们使用 [a-zA-Z0-9]+
    
#     # 字母，数字，符号（包括连字符-_）
#     # 只除去纯符号的行和纯数字的行
#     # 剩下字母，字母+符号(hand-made)，字母+数字(1st)，字母+数字+符号(www.123.com)，符号+数字(6:30)
    
#     # word_pattern = re.compile(r"^[a-zA-Z0-9]+$")
    
#     digit_pattern = re.compile(r"^[0-9]+$")
#     symbol_pattern = re.compile(r"^[^\w\s]+$")
    
#     # 用于存储符合条件的行
#     lines_to_keep = []

#     try:
#         with open(input_filename, 'r', encoding='utf-8') as infile:
#             for line in infile:
#                 # 1. 清除行末的换行符和可能的空白字符，得到实际的“word”
#                 stripped_line = line.strip() 

#                 # 2. 检查清理后的行是否符合“单词”模式
#                 if not stripped_line:
#                     continue
                
#                 if not digit_pattern.match(stripped_line) and not symbol_pattern.match(stripped_line):
#                     # 保留原始行（包含换行符），以便写入文件时保持格式
#                     lines_to_keep.append(line) 

#         # 写入 output.txt 文件
#         with open(output_filename, 'w', encoding='utf-8') as outfile:
#             outfile.writelines(lines_to_keep)

#         print(f"处理完成。已将过滤后的内容写入 {output_filename}")

#     except FileNotFoundError:
#         print(f"错误：找不到文件 {input_filename}")
#     except Exception as e:
#         print(f"发生错误: {e}")

# # 执行函数
# # filter_words()
# def main():
#     input_filename = []
#     # "input.txt"
#     if(len(sys.argv)==2):
#         input_filename = sys.argv[1]
#     elif(len(sys.argv) > 2):
#         print(f"Usage: python3 filter_words.py (可选)<输入文件名>")
#         exit(0)
#     else:
#         input_filename = "input.txt"
#     filter_words(input_filename=input_filename)  
    
# if __name__ == "__main__":
#     main()
    
def filter_words(input_dirpath="output_data/"):
    """
    读取 input 文件，删除所有非“单词”的行，并将结果写入 *.flt
    
    “单词”的定义：只包含字母（a-z, A-Z）和数字（0-9），且非空。
    """
    
    digit_pattern = re.compile(r"^[0-9]+$")
    symbol_pattern = re.compile(r"^[^\w\s]+$")
    


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
                    if not digit_pattern.match(stripped_line) and not symbol_pattern.match(stripped_line):
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