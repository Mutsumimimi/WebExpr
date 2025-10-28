#!/usr/bin/python3
import os

input_path = 'output_data/'
output_path = 'output_data/'

def generate_filelist():
    with open("filelist.txt", 'w', encoding='utf-8') as f:
        for filename in os.listdir(input_path):
            if filename.endswith('.desc'):
                f.write(f'../{input_path}{filename}')
                f.write('\n')
        print("成功生成 filelist.txt !")
            
generate_filelist()