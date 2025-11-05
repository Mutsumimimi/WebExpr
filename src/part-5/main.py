from collections import defaultdict
import os
import sys
import compress_index as Compress
import boolean_search_v2 as boolean_search   # 导入布尔检索模块


# --- 主运行函数 ---

def run():
    input_path = "output_data/"
    input_ending = '.stw' 
    BLOCK_SIZE = 4

    # 1. 文件读取与Token收集
    documents = Compress.read_documents(input_path, input_ending)
    
    # 2. 收集并排序所有唯一Token
    sorted_tokens = Compress.collect_and_sort_tokens(documents)

    # 3. 构建压缩词典和倒排索引
    global_term_string, final_dictionary, inverted_posting_lists = Compress.integrate_index_and_dictionary(
        documents=documents,
        sorted_tokens=sorted_tokens,
        BLOCK_SIZE=BLOCK_SIZE
    )
    term_string, dictionary_index = global_term_string, final_dictionary
    
    # --- 4. 基础结果演示 ---
    os.makedirs('./test', exist_ok=True)
    filename = "./test/compress_index_with_boolean.log"
    with open(filename, 'w', encoding='utf-8') as f:
        STDOUT = sys.stdout
        sys.stdout = f
        
        print("="*80)
        print("集成演示：文件读取 -> 词典压缩 -> 倒排索引 -> 布尔检索")
        print("="*80)
        
        print(f"\n[A] 收集到的唯一且排序后的Token (共 {len(sorted_tokens)} 个):")
        print(sorted_tokens[:20], "...")  # 只显示前20个
        
        print(f"\n[B] 压缩后的词典字符串 - 总长度: {len(term_string)}")
        print("-"*80)
        print(term_string[:200], "...")  # 只显示前200字符
        
        print(f"\n[C] 词典索引 (Anchor Token示例，前10个)")
        print("-"*80)
        for i, (token, entry) in enumerate(dictionary_index.items()):
            if i >= 10: break
            print(f"Anchor: '{token}' -> {entry}")
        
        # --- 5. 布尔检索演示 ---
        print("\n\n")
        print("="*80)
        print("布尔检索功能演示")
        print("="*80)
        
        # 初始化布尔检索引擎
        search_engine = boolean_search.BooleanSearchEngine(
            dictionary_index=dictionary_index,
            inverted_posting_lists=inverted_posting_lists
        )
        
        # 演示三种复杂查询
        boolean_search.demo_boolean_search(search_engine)
        # 新增短语查询
        boolean_search.demo_phrase_search(search_engine)
        
        # 性能分析
        test_queries = [
            "apple AND banana",
            "(apple OR banana) AND NOT chat",
            "(apple AND NOT banana) OR (chat AND date)"
        ]
        boolean_search.analyze_query_performance(search_engine, test_queries)
        
        # --- 6. 压缩效果分析 ---
        print("\n\n")
        print("="*80)
        print("存储空间对比摘要")
        print("="*80)
        
        original_token_length = sum(len(t) for t in sorted_tokens)
        compressed_string_length = len(term_string)
        
        print(f"Token总数: {len(sorted_tokens)}")
        print(f"词典块大小 (k): {BLOCK_SIZE}")
        print("-"*80)
        print(f"1. 词典字符串存储:")
        print(f"   - 原始存储: {original_token_length} 字符")
        print(f"   - 压缩存储: {compressed_string_length} 字符")
        compression_ratio = (1 - (compressed_string_length / original_token_length)) * 100
        print(f"   - 压缩率: {compression_ratio:.2f}%")
        print("-"*80)
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
        
        sys.stdout = STDOUT
        print(f"\n✓ 完整演示已写入 '{filename}'")
        print(f"✓ 支持的布尔操作: AND, OR, NOT, ()")
        print(f"✓ 示例查询: '(apple AND NOT banana) OR (chat AND date)'")

if __name__ == "__main__":
    run()