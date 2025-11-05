from nltk import word_tokenize, pos_tag
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

import os

def sample():
    porter = PorterStemmer()
    wnl = WordNetLemmatizer()
    
    word_list = ['play', 'playing', 'plays', 'played']
    extend_list = ['apples', 'active', 'information', 'mining', 'knowledge', 'brings']
    word_list += extend_list
    stem_list = []
    for str in word_list:
        stem_list.append(porter.stem(str))
    print(stem_list)
    # lemmatize_list = []
    lemmatize_list = [wnl.lemmatize(t) for t in word_list]
    print(lemmatize_list)
    
    raw_text = "The cars are running fast. He plays the games he liked."
    tokens = word_tokenize(raw_text)
    print(tokens)
    tagged_tokens = pos_tag(tokens)
    lemmatized_tokens = []
    for word, tag in tagged_tokens:
    # 获取 WordNet 词性
        w_net_pos = get_wordnet_pos(tag)
        lemma = wnl.lemmatize(word, w_net_pos)
        lemmatized_tokens.append(lemma)
    print(lemmatized_tokens)

input_path = "output_data/"
output_path = "output_data/"    # 路径
input_ending = '.flt'
output_ending = '.nml'  # 后缀名

def get_wordnet_pos(treebank_tag):
    """
    将 Penn Treebank POS 标签映射到 WordNet 的 POS 标签
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ         # 形容词 (a)
    elif treebank_tag.startswith('V'):
        return wordnet.VERB       # 动词 (v)
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN       # 名词 (n)
    elif treebank_tag.startswith('R'):
        return wordnet.ADV        # 副词 (r)
    else:
        # 对于其他词性（如介词、冠词、连词等），默认使用名词
        # WordNetLemmatizer 默认也会使用 'n'
        return wordnet.NOUN

def stemming(input_filepath, output_filepath):
    '''
    词干提取
    '''
    wnl = WordNetLemmatizer()
    with open(input_filepath, 'r', encoding='utf-8') as file:
        # orgn_tokens = file.readlines()
        # stem_tokens = []
        # for token in orgn_tokens:
        #     token = token.strip() # 去除换行符
        #     stem_tokens.append(wnl.lemmatize(token))
        orgn_lines = [line.strip() for line in file if line.strip()]
        
    tagged_tokens = pos_tag(orgn_lines)
    stem_tokens = []
    for word, tag in tagged_tokens:
        w_net_pos = get_wordnet_pos(tag)
        lemma = wnl.lemmatize(word, pos=w_net_pos)        
        stem_tokens.append(lemma)
        
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
# sample()