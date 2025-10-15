#!/home/ubuntu/Document/WebExpr/.venv/bin/python
# import nltk
import sys
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def sample():
    # nltk.download('stopwords')
    # nltk.download('punkt')

    # Sample text
    text = "This is a sample sentence showing stopword removal."

    # Get English stopwords and tokenize
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())

    # Remove stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]

    with open("debug.log", 'w', encoding='utf-8') as f:
        sys.stdout = f
        print("Original:", tokens)
        print("Filtered:", filtered_tokens)

    
input_path = 'output_data/'
output_path = 'output_data/'
input_ending = '.nml'
output_ending = '.stw'  # 后缀名

def tokenize():
    # Sample text
    # text = "This is a sample sentence showing stopword removal."
    for filename in os.listdir(input_path):
        with open(f'{input_path}{filename}', 'r', encoding='utf-8') as infile:
            text = infile.read()    
            
        # Get English stopwords and tokenize
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(text.lower())

        # Remove stopwords
        filtered_tokens = [word for word in tokens if word not in stop_words]

        basename, externname = os.path.splitext(filename)
        output_filename = f'{output_path}{basename}.tknz'
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            for i,filter_token in enumerate(filtered_tokens):
                f.write(filter_token)
                f.write("\n")
            # f.writelines(filtered_tokens)
            # sys.stdout = f
            # print("Original:", tokens)
            # print("Filtered:", filtered_tokens)
    
def clear(input_filepath, output_filepath):
    '''
    去除停用词
    '''
    tokens = []
    with open(input_filepath, 'r', encoding='utf-8') as file:
        # for i, str in enumerate(file):
        #     tokens[i] = str
        tokens = file.readlines()
        for i,token in enumerate(tokens):
            tokens[i] = tokens[i].strip() # 去除换行符
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # print(len(tokens))
    with open(output_filepath, 'w', encoding='utf-8') as f:
        for i, line in enumerate(filtered_tokens):
            f.write(line)
            f.write('\n')
        # original_stdout = sys.stdout
        # sys.stdout = f
        # print("Original:", tokens)
        # print("Filtered:", filtered_tokens)
        # sys.stdout = original_stdout
    print(f"已将去除停用词的内容写入 {output_filepath}")

def stopwd():
    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            input_filepath = f'{input_path}{input_filename}'
            basename, externname = os.path.splitext(input_filename)
            output_filepath = f'{input_path}{basename}{output_ending}'
            clear(input_filepath=input_filepath, output_filepath=output_filepath)
            
stopwd()