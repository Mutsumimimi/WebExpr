from nltk.stem import PorterStemmer
import os
def sample():
    porter = PorterStemmer()
    word_list = ['play', 'playing', 'plays', 'played']
    stem_list = []
    for str in word_list:
        stem_list.append(porter.stem(str))
    print(stem_list)

input_path = "output_data/"
output_path = "output_data/"    # 路径
input_ending = '.flt'
output_ending = '.nml'  # 后缀名

def stemming(input_filepath, output_filepath):
    '''
    词干提取
    '''
    porter = PorterStemmer()
    with open(input_filepath, 'r', encoding='utf-8') as file:
        orgn_tokens = file.readlines()
        stem_tokens = []
        for token in orgn_tokens:
            token = token.strip() # 去除换行符
            stem_tokens.append(porter.stem(token))
    with open(output_filepath, 'w', encoding='utf-8') as f:
        for token in stem_tokens:
            f.write(token)
            f.write('\n')

def run():
    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            input_filepath = f'{input_path}{input_filename}'
            basename, externname = os.path.splitext(input_filename)
            output_filepath = f'{input_path}{basename}{output_ending}'
            stemming(input_filepath=input_filepath, output_filepath=output_filepath)
            print(f"已将归一化的内容写入 {output_filepath}")
            
run()