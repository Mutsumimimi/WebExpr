from collections import defaultdict
import os
import sys
import skiplist


# 模拟 SkipList 的 df 计算 (简化)
def calculate_df_placeholder(token):
    return len(token) * 10 

# --- 词典压缩功能 ---

def front_code_and_block(sorted_tokens, block_size=4):
    """对有序Token列表进行前端编码和分块"""
    global_term_string = ""
    dictionary_index = {}
    
    current_block_id = 0
    current_offset = 0
    post_list_ref_counter = 1000

    for i in range(0, len(sorted_tokens), block_size):
        block_tokens = sorted_tokens[i:i + block_size]
        block_string_segment = ""
        anchor_token = block_tokens[0]
        
        # Anchor Token 编码
        anchor_encoding = f"0|{len(anchor_token)}|{anchor_token}"
        block_string_segment += anchor_encoding
        
        # 块内后续Token编码
        prev_token = anchor_token
        for j in range(1, len(block_tokens)):
            current_token = block_tokens[j]
            
            prefix_len = 0
            while prefix_len < len(prev_token) and prefix_len < len(current_token) and prev_token[prefix_len] == current_token[prefix_len]:
                prefix_len += 1
            
            suffix = current_token[prefix_len:]
            encoding = f"|{prefix_len}|{len(suffix)}|{suffix}"
            block_string_segment += encoding
            prev_token = current_token

        global_term_string += block_string_segment
        compressed_length = len(block_string_segment)
        
        entry = skiplist.DictionaryEntry(
            block_id=current_block_id,
            term_string_offset=current_offset,
            compressed_length=compressed_length,
            df=calculate_df_placeholder(anchor_token),
            post_list_ref=post_list_ref_counter
        )
        dictionary_index[anchor_token] = entry
        
        current_offset += compressed_length
        current_block_id += 1
        post_list_ref_counter += 1
        
    return global_term_string, dictionary_index

def reconstruct_token_from_string(block_data, index_in_block):
    """从压缩字符串中重建词项"""
    tokens = []
    parts = block_data.split('|')
    
    if len(parts) < 3: return None
    
    anchor_token = parts[2]
    tokens.append(anchor_token)
    
    current_prefix = anchor_token
    for i in range(3, len(parts), 3):
        if i + 2 >= len(parts): break
            
        try:
            prefix_len = int(parts[i])
            suffix = parts[i+2]
            next_token = current_prefix[:prefix_len] + suffix
            tokens.append(next_token)
            current_prefix = next_token
        except ValueError:
            break
        
    if index_in_block < len(tokens):
        return tokens[index_in_block]
    return None

# --- 文件读取与Token收集 ---

def read_documents(input_path, input_ending):
    """读取所有文件，收集文档ID、Token及其位置"""
    documents = {}

    for input_filename in os.listdir(input_path):
        if input_filename.endswith(input_ending):
            input_filepath = f'{input_path}{input_filename}'
            basename, _ = os.path.splitext(input_filename)
            
            token_with_pos = defaultdict(list)
            
            with open(input_filepath, 'r', encoding='utf-8') as file:
                for pos, line in enumerate(file):
                    token = line.strip()
                    if token:
                        token_with_pos[token].append(pos)
                documents[basename] = token_with_pos
            
    return documents


def collect_and_sort_tokens(documents):
    """收集所有唯一Token并排序"""
    all_tokens = set()
    for _, token_with_pos in documents.items():
        all_tokens.update(token_with_pos.keys())
    return sorted(list(all_tokens))

# 设定SkipList参数
MAX_LEVEL = 16 
P = 0.5

def invert_index(documents):
    """构建倒排索引"""
    inverted_index = defaultdict(lambda: skiplist.SkipList(max_level=MAX_LEVEL, p=P))
    
    for doc_id, token_with_pos in documents.items():
        for token, pos in token_with_pos.items():
            new_posting = skiplist.Value(doc_id, pos)
            inverted_index[token].insert(new_posting)

    return dict(inverted_index)

def integrate_index_and_dictionary(documents, sorted_tokens, BLOCK_SIZE):
    """集成倒排索引和压缩词典"""
    # 步骤1: 构建倒排索引
    inverted_posting_lists = invert_index(documents) 
    
    # 步骤2: 执行词典压缩
    global_term_string, dictionary_index = front_code_and_block(sorted_tokens, BLOCK_SIZE)
    
    # 步骤3: 关联SkipList实例到DictionaryEntry
    final_dictionary = {}
    
    for anchor_token, entry in dictionary_index.items():
        actual_skip_list = inverted_posting_lists[anchor_token] 
        entry.post_list_ref = actual_skip_list 
        final_dictionary[anchor_token] = entry
        
    return global_term_string, final_dictionary, inverted_posting_lists

# --- 主运行函数 ---
'''
单独测试压缩索引时，可以调用这个run()函数，跟main.py中的差不多
'''
def run():
    input_path = "output_data/"
    input_ending = '.stw' 
    BLOCK_SIZE = 4

    # 1. 文件读取与 Token 收集
    documents = read_documents(input_path, input_ending)
    
    # 2. 收集并排序所有唯一的 Token
    sorted_tokens = collect_and_sort_tokens(documents)

    # 3. 构建压缩词典
    # term_string, dictionary_index = front_code_and_block(sorted_tokens, BLOCK_SIZE)

    # 3.5 融入之前的倒排表设计
    global_term_string, final_dictionary, inverted_posting_lists = integrate_index_and_dictionary(
        documents=documents,
        sorted_tokens=sorted_tokens,
        BLOCK_SIZE=BLOCK_SIZE
    )
    term_string, dictionary_index = global_term_string, final_dictionary
    
    # --- 4. 结果演示 ---
    
    os.makedirs('./test', exist_ok=True)
    filename = "./test/compress_index.log"
    with open(filename, 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        print("--- 集成 Demo：文件读取 -> 词典压缩 (Front Coding & Blocking) ---")
        print(f"\n[A] 收集到的唯一且排序后的 Token (共 {len(sorted_tokens)} 个):")
        print(sorted_tokens)

        print(f"\n[B] 压缩后的词典字符串 (TERM_STRING) - 总长度: {len(term_string)}")
        print("----------------------------------------------------------------------------------------------------")
        print(term_string)
        print("----------------------------------------------------------------------------------------------------")

        print("\n[C] 词典索引 (仅存储 Anchor Token)")
        print("----------------------------------------------------------------------------------------------------")
        for token, entry in dictionary_index.items():
            print(f"Anchor Token: '{token}' -> {entry}")
        print("----------------------------------------------------------------------------------------------------")

        # --- 查询演示 ---
        
        # 1. 查找 'apricot' (Block 0, Anchor 'apple')
        query_token = 'archer'
        anchor_token_for_query = 'april' # 手动查找 Anchor Token
        
        if anchor_token_for_query in dictionary_index:
            entry = dictionary_index[anchor_token_for_query]
            block_data = term_string[entry.term_string_offset : entry.term_string_offset + entry.compressed_length]
            
            # 查找 'archer' 在 Block 0 中的索引 (['apple', 'apply', 'apricot', 'banana']) -> 2
            reconstructed = reconstruct_token_from_string(block_data, 2)
            print(f"\n查询演示：查找 '{query_token}'")
            print(f"  使用 Anchor: '{anchor_token_for_query}', 重建结果: '{reconstructed}'")
        else:
            print(f"\n警告：Anchor Token '{anchor_token_for_query}' 不存在于词典索引中。")

        sys.stdout = STDOUT
        print(f"词典压缩方案已成功演示，结果已写入 '{filename}'")

    # --- 5. 压缩结果分析 ---
    # --- 在 run 函数的末尾添加以下输出 ---

    original_token_length = sum(len(t) for t in sorted_tokens)
    compressed_string_length = len(term_string)

    print("\n\n--- 存储空间对比摘要 ---")
    print(f"Token 总数: {len(sorted_tokens)}")
    print(f"词典块大小 (k): {BLOCK_SIZE}")
    print("-----------------------------------")
    print(f"1. 词典字符串存储:")
    print(f"   - 原索引 (所有 Token 字符串): {original_token_length} 字符/字节")
    print(f"   - 压缩后 (global_term_string): {compressed_string_length} 字符/字节")
    compression_ratio = (1 - (compressed_string_length / original_token_length)) * 100
    print(f"   - 压缩率: {compression_ratio:.2f}%")
    print("-----------------------------------")
    print("2. 倒排记录表存储:")
    print(f"2. 倒排索引统计:")
    print(f"   - 总词项数: {len(inverted_posting_lists)}")
    
    total_postings = 0
    for skip_list in inverted_posting_lists.values():
        current = skip_list.header.forward[0]
        while current:
            total_postings += 1
            current = current.forward[0]
    
    print(f"   - 总posting数: {total_postings}")
    print(f"   - 平均每词项posting数: {total_postings/len(inverted_posting_lists):.2f}")


if __name__ == "__main__":
    # Note: 假设 SkipList/Node 类不影响此处的词典构建逻辑
    run()