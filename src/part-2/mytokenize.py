from nltk.tokenize import word_tokenize
import os

def tokenize(input_filepath, output_filepath):
    tokens = []
    with open(input_filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                tokens_by_line= word_tokenize(line)
                # tokens.append(tokens_by_line)
                tokens += tokens_by_line
    with open(output_filepath, 'w', encoding='utf-8') as f:
        for token in tokens:
            f.write(token)
            f.write('\n')

input_path = "output_data/"     # 路径
input_ending = '.desc'          # 后缀名
output_path = "output_data/"    
output_ending = '.conll'  

def run():
    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            input_filepath = f'{input_path}{input_filename}'
            output_filepath = f'{input_path}{input_filename}{output_ending}'
            tokenize(input_filepath=input_filepath, output_filepath=output_filepath)
            print(f"已将 tokenize 后的内容写入 {output_filepath}")

run()