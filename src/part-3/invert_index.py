from collections import defaultdict
import os
import sys
import skiplist

def sample():
    # Define the documents
    document1 = "The quick brown fox jumped over the lazy dog."
    document2 = "The lazy dog slept in the sun."

    # Step 1: Tokenize the documents
    # Convert each document to lowercase and split it into words
    tokens1 = document1.lower().split()
    tokens2 = document2.lower().split()

    # Combine the tokens into a list of unique terms
    terms = list(set(tokens1 + tokens2))

    # Step 2: Build the inverted index
    # Create an empty dictionary to store the inverted index
    inverted_index = {}

    # For each term, find the documents that contain it
    for term in terms:
        documents = []
        if term in tokens1:
            documents.append("Document 1")
        if term in tokens2:
            documents.append("Document 2")
        inverted_index[term] = documents

    # Step 3: Print the inverted index
    for term, documents in inverted_index.items():
        print(term, "->", ", ".join(documents))

# 设定 SkipList 的参数
MAX_LEVEL = 16 
P = 0.5

def invert_index(documents):
    '''
    输入：type=dictionary
    { 
      1：['i', 'am', 'a', 'student']
      2: ['i', 'have', 'a', 'computer']
      ...
    }
    输出：type=dictionary
    { 
      'i':  [doc1, doc2]
      'am': [doc1]
      'a':  [doc1, doc2]
      ...
    }
    '''
    inverted_index = defaultdict(list)
    # 遍历所有文档及其 ID
    for doc_id, tokens in documents.items():        
        # 使用 set() 来确保每个文档 ID 在 Posting List 中只出现一次
        # 即使同一个词在一个文档中出现多次
        unique_tokens = (set(tokens))

        # 遍历文档中的唯一 Token
        for token in unique_tokens:
            # 将当前文档 ID 添加到该 Token 的 Posting List 中
            token = token.strip()
            inverted_index[token].append(doc_id)

    return inverted_index

def add_skiplist(temp_index):
    final_inverted_index = {}

    # 第二次遍历：将每个 Token 的文档 ID 列表转换为 SkipList
    for token, doc_ids in temp_index.items():
        # 1. 确保文档 ID 列表有序 (SkipList 依赖于有序插入)
        doc_ids.sort() 
        
        # 2. 创建一个新的 SkipList 实例作为 Posting List
        skip_list = skiplist.SkipList(max_level=MAX_LEVEL, p=P)
        
        # 3. 将所有文档 ID 插入到 SkipList 中
        for doc_id in doc_ids:
            # 注意: SkipList 默认不支持重复值。在倒排索引中，同一个 doc_id 
            # 只应被插入一次 (已通过 set(tokens) 确保)
            skip_list.insert(doc_id) 
            
        final_inverted_index[token] = skip_list 

    return final_inverted_index

input_path = "output_data/"
input_ending = '.stw'

def print_token(index):
    os.makedirs('./test', exist_ok=True)
    with open("./test/all_token.log", 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        # 遍历 Token (键) 的字典序
        for token, skip_list in sorted(index.items()):
            doc_ids = []
            if skip_list:
                current = skip_list.header.forward[0] # 从底层链表的头节点开始
                while current:
                    doc_ids.append(current.value)
                    current = current.forward[0]
            print(f"{token}")
            
        sys.stdout = STDOUT
        print("已打印所有文档中的全部 token ！")

def run():
    documents = {}  # 创建空字典，作为倒排表的输入
    
    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            # 找到对应的输入文件
            
            input_filepath = f'{input_path}{input_filename}'
            basename, externname = os.path.splitext(input_filename)
            
            with open(input_filepath, 'r', encoding='utf-8') as file:
                tokens = [line.strip() for line in file.readlines()]
                documents[basename] = tokens
    
    # 得到倒排表
    temp_index = invert_index(documents=documents)
    final_inverted_index = add_skiplist(temp_index=temp_index)
    # 打印
    os.makedirs('./test', exist_ok=True)
    print_token(index=final_inverted_index)
    with open("./test/inverted_index.log", 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        # # 打印初始倒排表 
        # for id, elem in final_inverted_index.items():
        #     print(id, ':\t', elem)
        
        # 遍历 Token (键) 的字典序
        for token, skip_list in sorted(final_inverted_index.items()):
            
            # 遍历 SkipList 的底层链表 (level 0) 来收集文档 ID
            doc_ids = []
            if skip_list:
                current = skip_list.header.forward[0] # 从底层链表的头节点开始
                while current:
                    doc_ids.append(current.value)
                    current = current.forward[0]
            
            # 打印格式：Token : [有序的文档 ID 列表]
            # 注意：这里我们只打印了 doc_id 列表，没有打印跳表指针本身，
            # 因为 SkipList 的指针是内部结构，直接打印列表即可验证其正确性。
            print(f"{token}:\t{doc_ids}")
            
        sys.stdout = STDOUT
        print("已得到带有skip list的倒排表！")

if __name__ == "__main__":
    run()