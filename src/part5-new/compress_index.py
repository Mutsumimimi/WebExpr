from collections import defaultdict
import os
import sys
import skiplist


# 模拟 SkipList 的 df 计算 (简化)
def calculate_df_placeholder(token):
    # 实际应从 SkipList 中计算，这里使用 token 长度的倍数作为占位符
    return len(token) * 10 

# --- 词典压缩功能 (来自之前的实现) ---

def front_code_and_block(sorted_tokens, block_size=4):
    """
    对有序 Token 列表进行前端编码和分块，并构建词典。
    """
    global_term_string = ""
    dictionary_index = {}
    
    current_block_id = 0
    current_offset = 0
    post_list_ref_counter = 1000 # PostList-ref 指针占位符

    for i in range(0, len(sorted_tokens), block_size):
        block_tokens = sorted_tokens[i:i + block_size]
        
        block_string_segment = ""
        anchor_token = block_tokens[0]
        
        # Anchor Token 编码: 0|Anchor_Length|Anchor_Token
        anchor_encoding = f"0|{len(anchor_token)}|{anchor_token}"
        block_string_segment += anchor_encoding
        
        # 块内后续 Token 编码
        prev_token = anchor_token
        for j in range(1, len(block_tokens)):
            current_token = block_tokens[j]
            
            # 计算前缀长度 (P)
            prefix_len = 0
            while prefix_len < len(prev_token) and prefix_len < len(current_token) and prev_token[prefix_len] == current_token[prefix_len]:
                prefix_len += 1
            
            # 计算后缀 (Suffix)
            suffix = current_token[prefix_len:]
            
            # 格式: |P|Suffix_Length|Suffix
            encoding = f"|{prefix_len}|{len(suffix)}|{suffix}"
            block_string_segment += encoding
            
            prev_token = current_token

        # 按块存储 (Blocking)
        global_term_string += block_string_segment
        compressed_length = len(block_string_segment)
        
        # 只为 Anchor Token 创建词典条目
        entry = skiplist.DictionaryEntry(
            block_id=current_block_id,
            term_string_offset=current_offset,
            compressed_length=compressed_length,
            df=calculate_df_placeholder(anchor_token),
            post_list_ref=post_list_ref_counter
        )
        dictionary_index[anchor_token] = entry
        
        # 更新偏移量和计数器
        current_offset += compressed_length
        current_block_id += 1
        post_list_ref_counter += 1
        
    return global_term_string, dictionary_index

def reconstruct_token_from_string(block_data, index_in_block):
    """
    从压缩字符串中重建词项，用于查询演示。
    """
    tokens = []
    
    parts = block_data.split('|')
    
    # 锚点 Token
    if len(parts) < 3: return None
    
    anchor_token = parts[2]
    tokens.append(anchor_token)
    
    current_prefix = anchor_token
    # 遍历后续 Token (从索引 3 开始，每 3 个元素一组：P, L, Suffix)
    for i in range(3, len(parts), 3):
        if i + 2 >= len(parts): break
            
        try:
            prefix_len = int(parts[i])
            # suffix_len = int(parts[i+1]) # 长度信息在解析中可以忽略
            suffix = parts[i+2]
            
            next_token = current_prefix[:prefix_len] + suffix
            tokens.append(next_token)
            current_prefix = next_token
        except ValueError:
            # 数据格式错误，中断解析
            break
        
    if index_in_block < len(tokens):
        return tokens[index_in_block]
    return None

# --- 文件读取与 Token 收集逻辑 ---

def read_documents(input_path, input_ending):
    """
    读取所有文件，收集文档 ID、Token 及其位置。
    返回: documents = {doc_id: {token: [pos1, pos2, ...]}}
    """
    documents = {}

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
            
    return documents


def collect_and_sort_tokens(documents):
    """
    从所有文档中收集所有唯一的 Token，并按字典序排序。
    """
    all_tokens = set()
    for _, token_with_pos in documents.items():
        all_tokens.update(token_with_pos.keys())
        
    return sorted(list(all_tokens))

# 设定 SkipList 的参数
MAX_LEVEL = 16 
P = 0.5

def invert_index(documents):
    '''
    从documents字典构建关于token的倒排表. token := SkipList
    '''
    inverted_index = defaultdict(lambda: skiplist.SkipList(max_level=MAX_LEVEL, p=P))
    # 遍历所有文档及其 ID
    for doc_id, token_with_pos in documents.items():

        # for token, pos in sorted(token_with_pos.items()):
        for token, pos in (token_with_pos.items()):
            
            new_posting = skiplist.Value(doc_id, pos)
            inverted_index[token].insert(new_posting)

    return dict(inverted_index)

def integrate_index_and_dictionary(documents, sorted_tokens, BLOCK_SIZE):
    
    # 步骤 1: 构建所有 Token 的 SkipList 实例
    inverted_posting_lists = invert_index(documents) 
    
    # 步骤 2: 执行词典压缩和分块，获取压缩字符串和 Anchor 字典
    # 注意：我们保留了 front_code_and_block 的压缩逻辑，但需要在最后设置真实的指针
    global_term_string, dictionary_index = front_code_and_block(sorted_tokens, BLOCK_SIZE)
    
    # 步骤 3: 关联真实的 SkipList 实例到 DictionaryEntry
    final_dictionary = {}
    
    for anchor_token, entry in dictionary_index.items():
        # 注意：这里假设 Anchor Token 在 inverted_posting_lists 中存在
        # 获取该 Anchor Token 对应的 SkipList 实例
        actual_skip_list = inverted_posting_lists[anchor_token] 
        
        # 将 DictionaryEntry 的 post_list_ref 指向这个 SkipList 实例
        # 这是最简单的"指针"实现
        entry.post_list_ref = actual_skip_list 
        
        # 实际的 DF 也可以从 SkipList 中重新计算（如果需要）
        # entry.document_frequency = actual_skip_list.calculate_df() 
        
        final_dictionary[anchor_token] = entry
        
    return global_term_string, final_dictionary

# --- 主运行函数 ---

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
    global_term_string, final_dictionary = integrate_index_and_dictionary(
        documents=documents,
        sorted_tokens=sorted_tokens,
        BLOCK_SIZE=BLOCK_SIZE
    )
    term_string, dictionary_index = global_term_string, final_dictionary
    
    # --- 4. 结果演示 ---
    
    os.makedirs('./test', exist_ok=True)
    filename = "./test/compress_index-2.log"
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
    print("   - 无法精确计算，因为未实现压缩编码 (Var-Byte/Gamma)")
    print("   - 概念效果: 文档ID和位置信息经差值编码后，存储空间将大幅减小。")

if __name__ == "__main__":
    # Note: 假设 SkipList/Node 类不影响此处的词典构建逻辑
    run()