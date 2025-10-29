from collections import defaultdict
import os
import sys
sys.path.append('src/part-4/')
import skiplist

'''
为上一阶段已经带有跳表索引的倒排表，添加位置信息

token:= SkipList
        ├── max_level: 跳表的最大层数
        ├── p: 第i层的任一元素在第i+1层出现的概率
        ├── header: 头节点(Node类型)
        │   ├── header.value: 元素的值，在 inverted_list 中是文档序号 doc_id
        │   └── header.forward: 元素个数为 level+1 的数组, forward[i] 表示第i层的节点的后继
        └── level: 节点的层数，表示某个元素有几个(层)跳表节点

class value:            
{
    'doc_id': 1,
    'positions': [3, 15, 22]  # 词项在文档 1 中出现的位置
}
'''
    
input_path = "output_data/"
input_ending = '.stw'    

# 设定 SkipList 的参数
MAX_LEVEL = 16 
P = 0.5

def invert_index(documents):
    
    inverted_index = defaultdict(lambda: skiplist.SkipList(max_level=MAX_LEVEL, p=P))
    # 遍历所有文档及其 ID
    for doc_id, token_with_pos in documents.items():

        for token, pos in (token_with_pos.items()):
            
            new_posting = skiplist.Value(doc_id, pos)
           
            # skip_list = inverted_index[token]
            # skip_list.insert(new_posting)
            inverted_index[token].insert(new_posting)

    return dict(inverted_index)

def run():
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
    
    # 得到倒排表
    inverted_index = invert_index(documents=documents)

    # 打印
    os.makedirs('./test', exist_ok=True)
    with open("./test/part-4.log", 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        # 遍历 Token (键) 的字典序
        for token, skip_list in sorted(inverted_index.items()):
            
            # 遍历 SkipList 的底层链表 (level 0)
            posting_list_info = []
            if skip_list:
                current = skip_list.header.forward[0]
                while current:
                    # 从 Node.value 中提取 doc_id 和 positions
                    doc_id = current.value.id
                    positions = current.value.pos
                    
                    # 格式化输出：(文档ID: [位置列表])
                    posting_list_info.append(f"({doc_id}: {positions})")
                    current = current.forward[0]
            
            # 打印格式：Token: [ (doc_id: [pos]), (doc_id: [pos]), ... ]
            print(f"{token}:\t{' -> '.join(posting_list_info)}")
            
        sys.stdout = STDOUT
        print("已得到带有skip list和词项位置信息的倒排表！")
        print("已写入到 ./test/part-4.log 中.")
        
if __name__ == "__main__":
    run()