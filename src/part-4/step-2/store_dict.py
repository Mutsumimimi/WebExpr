from collections import defaultdict
import os
import sys
import skiplist
import DictEntry

'''
这个文件暂时没有用。skiplist无法静态 I/O
'''
MAX_LEVEL = 5 
P = 0.5

def invert_index_and_build_dictionary(documents):
    """
    首先构建 SkipList Posting List，然后创建词典条目。
    
    返回: { token: DictionaryEntry 实例 }
    """
    # 步骤 1: 构建 SkipList Posting List (和之前一样)
    inverted_posting_lists = defaultdict(lambda: skiplist.SkipList(max_level=MAX_LEVEL, p=P))
    
    for doc_id, token_with_pos in documents.items():
        for token, pos in token_with_pos.items():
            new_posting = skiplist.Value(doc_id, pos)
            inverted_posting_lists[token].insert(new_posting)
            
    # 步骤 2: 构建词典
    inverted_dictionary = {}
    
    for token, skip_list_instance in inverted_posting_lists.items():
        # 创建词典条目，并将 SkipList 实例作为指针存储
        entry = DictEntry.DictionaryEntry(token, skip_list_instance)
        inverted_dictionary[token] = entry
        
    return dict(inverted_dictionary)

# 注意：您需要将 run() 函数中对 invert_index 的调用改为 invert_index_and_build_dictionary。

# ... (run 函数的前半部分，文件读取和构建 documents 字典的代码保持不变) ...

input_path = "output_data/"
input_ending = '.stw'    

def run():
    # ... (文件读取代码，构建 documents 字典) ...
    documents = {}  # 创建空字典，作为倒排表的输入
    
    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            # 找到对应的输入文件
            
            input_filepath = f'{input_path}{input_filename}'
            basename, _ = os.path.splitext(input_filename)
            
            token_with_pos = defaultdict(list)
            
            with open(input_filepath, 'r', encoding='utf-8') as file:
                # 使用 enumerate 记录位置 (pos)
                # pos 即为行号 - 1，从 0 开始计数
                for pos, line in enumerate(file):
                    token = line.strip()
                    if token:
                        # 记录 Token 及其在文档中的位置
                        token_with_pos[token].append(pos)
                # documents 字典现在存储每个文档的 (Token: 位置列表) 映射
                documents[basename] = token_with_pos
    # 得到倒排词典 (调用新函数)
    inverted_dictionary = invert_index_and_build_dictionary(documents=documents)
    
    # 打印
    os.makedirs('./test', exist_ok=True)
    with open("./test/dictionary_solution.log", 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        # 遍历 Token (键) 的字典序
        print("--- 倒排索引词典 ---")
        
        # 确保按 Token 字典序输出
        for token, entry in sorted(inverted_dictionary.items()): 
            
            # 从 DictionaryEntry 中获取 Posting List 实例
            skip_list = entry.PostList_ref
            
            # 遍历 SkipList 的底层链表，提取 Posting 信息
            posting_info = []
            if skip_list:
                current = skip_list.header.forward[0]
                while current:
                    doc_id = current.value.id
                    positions = current.value.pos
                    posting_info.append(f"({doc_id}: {positions})")
                    current = current.forward[0]
            
            # 打印词典元数据和 Posting List (Posting List 对应于倒排记录表的内容)
            print(f"\nTOKEN: {token}")
            # 文档频率
            print(f"  DF: {entry.document_frequency}") 
            # 指针
            print(f"  PL_REF: SkipList @ Level {entry.PostList_ref.level}")
            # 倒排索引指针
            print(f"  POSTING LIST: {' -> '.join(posting_info)}")
            
        sys.stdout = STDOUT
        print("词典存储方案已成功演示，结果已写入 ./test/dictionary_solution.log")

if __name__ == "__main__":
    run()