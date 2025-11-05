'''
part5 第二部分 向量空间模型
'''

"""
TF-IDF与向量空间模型测试脚本
完整测试排名检索功能
"""

import skiplist
import boolean_search
import tfidf_vector_space
import compress_index as Compress


def create_test_data():
    """创建测试数据集"""
    test_documents = {
        # 信息检索主题文档
        "ir_doc1": {
            "information": [0, 10, 20],
            "retrieval": [1, 11, 21],
            "system": [2, 15],
            "search": [5],
            "document": [8, 18]
        },
        "ir_doc2": {
            "information": [0, 8],
            "retrieval": [1, 9],
            "model": [4],
            "vector": [5],
            "space": [6]
        },
        "ir_doc3": {
            "search": [0],
            "engine": [1],
            "web": [2],
            "information": [5],
            "document": [10]
        },
        
        # 数据挖掘主题文档
        "dm_doc1": {
            "data": [0, 12, 25],
            "mining": [1, 13, 26],
            "algorithm": [5],
            "pattern": [8],
            "knowledge": [15]
        },
        "dm_doc2": {
            "data": [2, 10],
            "mining": [3],
            "machine": [6],
            "learning": [7],
            "model": [12]
        },
        "dm_doc3": {
            "algorithm": [0, 15],
            "data": [5],
            "structure": [8],
            "analysis": [12]
        },
        
        # 机器学习主题文档
        "ml_doc1": {
            "machine": [0, 10],
            "learning": [1, 11],
            "algorithm": [5],
            "neural": [8],
            "network": [9]
        },
        "ml_doc2": {
            "machine": [2],
            "learning": [3],
            "model": [6],
            "training": [10],
            "data": [15]
        },
        
        # 混合主题文档
        "mix_doc1": {
            "information": [0],
            "retrieval": [1],
            "data": [5],
            "mining": [6],
            "system": [10]
        },
        "mix_doc2": {
            "search": [0],
            "algorithm": [5],
            "machine": [8],
            "learning": [9]
        }
    }
    
    return test_documents


def build_inverted_index(test_documents):
    """构建倒排索引"""
    inverted_posting_lists = {}
    MAX_LEVEL = 16
    P = 0.5
    
    all_tokens = set()
    for doc_tokens in test_documents.values():
        all_tokens.update(doc_tokens.keys())
    
    for token in all_tokens:
        skip_list = skiplist.SkipList(max_level=MAX_LEVEL, p=P)
        
        for doc_id, doc_tokens in test_documents.items():
            if token in doc_tokens:
                positions = doc_tokens[token]
                posting = skiplist.Value(doc_id, positions)
                skip_list.insert(posting)
        
        inverted_posting_lists[token] = skip_list
    
    dictionary_index = {}
    for i, token in enumerate(sorted(all_tokens)):
        entry = skiplist.DictionaryEntry(
            block_id=i // 4,
            term_string_offset=i * 10,
            compressed_length=10,
            df=0,
            post_list_ref=inverted_posting_lists[token]
        )
        dictionary_index[token] = entry
    
    return inverted_posting_lists, dictionary_index


def print_data_statistics(test_documents, inverted_posting_lists):
    """打印数据统计信息"""
    print("="*100)
    print("测试数据集统计")
    print("="*100)
    
    print(f"\n文档数: {len(test_documents)}")
    print(f"词项数: {len(inverted_posting_lists)}")
    
    print(f"\n文档主题分布:")
    print(f"  信息检索: 3个文档 (ir_doc1, ir_doc2, ir_doc3)")
    print(f"  数据挖掘: 3个文档 (dm_doc1, dm_doc2, dm_doc3)")
    print(f"  机器学习: 2个文档 (ml_doc1, ml_doc2)")
    print(f"  混合主题: 2个文档 (mix_doc1, mix_doc2)")


def test_tfidf_calculation(vsm):
    """测试TF-IDF计算"""
    print("\n\n" + "="*100)
    print("【测试1】TF-IDF计算验证")
    print("="*100)
    
    test_terms = ["apple", "data", "air", "learn"]
    
    print(f"\n{'词项':<20} {'文档频率':<15} {'IDF值':<15} {'说明':<30}")
    print("-"*100)
    
    for term in test_terms:
        info = vsm.get_term_info(term)
        df = info['document_frequency']
        idf = info['idf']
        
        if df == 0:
            desc = "未出现"
        elif df <= 2:
            desc = "罕见词（高IDF）"
        elif df <= 5:
            desc = "常见词（中等IDF）"
        else:
            desc = "高频词（低IDF）"
        
        print(f"{term:<20} {df:<15} {idf:<15.4f} {desc:<30}")


def test_document_vectors(vsm):
    """测试文档向量"""
    print("\n\n" + "="*100)
    print("【测试2】文档向量分析")
    print("="*100)
    
    sample_docs = ["ir_doc1", "dm_doc1", "ml_doc1"]
    sample_docs = ["10550930", "10550943", "10552722"]
    
    for doc_id in sample_docs:
        info = vsm.get_document_info(doc_id)
        if info:
            print(f"\n{'-'*100}")
            print(f"文档ID: {doc_id}")
            print(f"  文档长度: {info['length']} 个词")
            print(f"  唯一词项数: {info['num_unique_terms']}")
            print(f"  向量范数: {info['norm']:.4f}")
            print(f"  Top-3权重词项:")
            for term, weight in info['top_terms'][:3]:
                print(f"    {term}: {weight:.4f}")


def test_ranked_retrieval(vsm):
    """测试排名检索"""
    print("\n\n" + "="*100)
    print("【测试3】排名检索测试")
    print("="*100)
    
    queries = [
        (["information", "retrieval"], "信息检索主题"),
        (["data", "mining"], "数据挖掘主题"),
        (["machine", "learning"], "机器学习主题"),
        (["algorithm", "data"], "算法与数据"),
        (["search", "system"], "搜索系统"),
    ]
    
    for query_terms, description in queries:
        print(f"\n{'-'*100}")
        print(f"查询: {' '.join(query_terms)} ({description})")
        
        results = vsm.search(query_terms, top_k=5)
        
        if results:
            print(f"\nTop-{len(results)} 结果:")
            for i, (doc_id, score) in enumerate(results, 1):
                print(f"  {i}. {doc_id:<15} 得分: {score:.4f}")
        else:
            print("  无匹配结果")


def test_query_expansion(vsm):
    """测试查询扩展效果"""
    print("\n\n" + "="*100)
    print("【测试4】查询长度对结果的影响")
    print("="*100)
    
    base_query = ["information"]
    expanded_queries = [
        ["information"],
        ["information", "retrieval"],
        ["information", "retrieval", "system"],
    ]
    
    for query_terms in expanded_queries:
        print(f"\n{'-'*100}")
        print(f"查询: {' '.join(query_terms)}")
        
        results = vsm.search(query_terms, top_k=3)
        
        if results:
            print(f"结果:")
            for i, (doc_id, score) in enumerate(results, 1):
                print(f"  {i}. {doc_id:<15} 得分: {score:.4f}")


def test_similarity_comparison(vsm):
    """测试文档间相似度"""
    print("\n\n" + "="*100)
    print("【测试5】文档相似度比较")
    print("="*100)
    
    doc_pairs = [
        ("ir_doc1", "ir_doc2", "同主题文档"),
        ("ir_doc1", "dm_doc1", "不同主题文档"),
        ("dm_doc1", "dm_doc2", "同主题文档"),
        ("ml_doc1", "ml_doc2", "同主题文档"),
    ]
    
    print(f"\n{'文档对':<30} {'类型':<20} {'余弦相似度':<15}")
    print("-"*100)
    
    for doc1_id, doc2_id, doc_type in doc_pairs:
        doc1 = vsm.doc_vectors.get(doc1_id)
        doc2 = vsm.doc_vectors.get(doc2_id)
        
        if doc1 and doc2:
            similarity = doc1.cosine_similarity(doc2)
            print(f"{doc1_id} - {doc2_id}".ljust(30) + 
                  f"{doc_type:<20} {similarity:.4f}")


def test_boolean_vs_ranked(ranked_retrieval):
    """对比布尔检索和排名检索"""
    print("\n\n" + "="*100)
    print("【测试6】布尔检索 vs 排名检索")
    print("="*100)
    
    test_queries = [
        "information AND retrieval",
        "data AND mining",
        "machine AND learning"
    ]
    
    for query in test_queries:
        print(f"\n{'-'*100}")
        print(f"查询: {query}")
        
        # 布尔检索
        boolean_result = ranked_retrieval.search(query, mode='boolean')
        print(f"\n布尔检索结果 (无排序):")
        print(f"  匹配文档: {sorted(boolean_result)}")
        print(f"  文档数: {len(boolean_result)}")
        
        # 排名检索
        query_terms = query.replace(" AND ", " ").split()
        ranked_result = ranked_retrieval.search(query_terms, mode='ranked', top_k=5)
        print(f"\n排名检索结果 (TF-IDF排序):")
        if ranked_result:
            for i, (doc_id, score) in enumerate(ranked_result, 1):
                print(f"  {i}. {doc_id:<15} 得分: {score:.4f}")
        else:
            print("  无结果")


def test_different_tf_schemes(inverted_posting_lists):
    """对比不同TF计算方案"""
    print("\n\n" + "="*100)
    print("【测试7】不同TF计算方案对比")
    print("="*100)
    
    schemes = ['raw', 'log', 'boolean', 'augmented']
    query_terms = ["information", "retrieval"]
    
    print(f"\n查询: {' '.join(query_terms)}\n")
    
    for scheme in schemes:
        print(f"{'-'*100}")
        print(f"TF方案: {scheme}")
        
        vsm_temp = tfidf_vector_space.VectorSpaceModel(
            inverted_posting_lists, 
            tf_scheme=scheme, 
            idf_scheme='standard'
        )
        
        results = vsm_temp.search(query_terms, top_k=3)
        
        if results:
            print(f"Top-3 结果:")
            for i, (doc_id, score) in enumerate(results, 1):
                print(f"  {i}. {doc_id:<15} 得分: {score:.4f}")


def test_performance_analysis(vsm):
    """性能分析"""
    print("\n\n" + "="*100)
    print("【测试8】性能特性分析")
    print("="*100)
    
    import time
    
    queries = [
        ["information"],                              # 单词查询
        ["information", "retrieval"],                 # 二词查询
        ["information", "retrieval", "system"],       # 三词查询
        ["data", "mining", "algorithm", "pattern"],   # 四词查询
    ]
    
    print(f"\n{'查询长度':<15} {'查询词项':<50} {'耗时(ms)':<15} {'结果数':<10}")
    print("-"*100)
    
    for query_terms in queries:
        start = time.perf_counter()
        
        # 执行多次取平均
        for _ in range(100):
            results = vsm.search(query_terms, top_k=10)
        
        end = time.perf_counter()
        avg_time = (end - start) / 100 * 1000
        
        query_str = ' '.join(query_terms)
        print(f"{len(query_terms)}词".ljust(15) + 
              f"{query_str:<50} {avg_time:>8.4f}      {len(results):<10}")


def analyze_results_quality(vsm):
    """分析结果质量"""
    print("\n\n" + "="*100)
    print("【测试9】结果质量分析")
    print("="*100)
    
    # 预期结果（人工标注）
    expected = {
        "information retrieval": ["ir_doc1", "ir_doc2", "mix_doc1"],
        "data mining": ["dm_doc1", "dm_doc2", "mix_doc1"],
        "machine learning": ["ml_doc1", "ml_doc2", "mix_doc2"]
    }
    
    for query_str, expected_docs in expected.items():
        query_terms = query_str.split()
        results = vsm.search(query_terms, top_k=5)
        
        retrieved_docs = [doc_id for doc_id, _ in results]
        
        # 计算精确率和召回率
        relevant_retrieved = len(set(retrieved_docs) & set(expected_docs))
        precision = relevant_retrieved / len(retrieved_docs) if retrieved_docs else 0
        recall = relevant_retrieved / len(expected_docs) if expected_docs else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n{'-'*100}")
        print(f"查询: {query_str}")
        print(f"预期相关文档: {expected_docs}")
        print(f"检索到的文档: {retrieved_docs}")
        print(f"精确率 (Precision): {precision:.2%}")
        print(f"召回率 (Recall): {recall:.2%}")
        print(f"F1得分: {f1:.2%}")


def main():
    """主测试函数"""
    print("\n" + "="*100)
    print(" "*35 + "TF-IDF与向量空间模型测试")
    print("="*100)
    
    # 1. 准备数据
    print("\n正在准备测试数据...")
    # test_documents = create_test_data()
    
    input_path = "output_data/"
    input_ending = '.stw' 
    test_documents = Compress.read_documents(input_path, input_ending)
    
    print(f"✓ 已生成 {len(test_documents)} 个测试文档")
    
    print("正在构建倒排索引...")
    inverted_posting_lists, dictionary_index = build_inverted_index(test_documents)
    print(f"✓ 已索引 {len(inverted_posting_lists)} 个词项")
    
    # 打印统计信息
    print_data_statistics(test_documents, inverted_posting_lists)
    
    # 2. 构建VSM
    print("\n正在构建向量空间模型...")
    vsm = tfidf_vector_space.VectorSpaceModel(
        inverted_posting_lists,
        tf_scheme='log',
        idf_scheme='standard'
    )
    
    # 3. 初始化布尔检索引擎
    print("正在初始化布尔检索引擎...")
    boolean_engine = boolean_search.BooleanSearchEngine(
        dictionary_index=dictionary_index,
        inverted_posting_lists=inverted_posting_lists
    )
    
    # 4. 初始化排名检索引擎
    print("正在初始化排名检索引擎...")
    ranked_retrieval = tfidf_vector_space.RankedRetrieval(boolean_engine, vsm)
    print("✓ 所有组件初始化完成\n")
    
    # 5. 运行测试
    input("按 Enter 键开始测试...")
    
    test_tfidf_calculation(vsm)
    input("\n按 Enter 继续...")
    
    test_document_vectors(vsm)
    input("\n按 Enter 继续...")
    
    test_ranked_retrieval(vsm)
    input("\n按 Enter 继续...")
    
    test_query_expansion(vsm)
    input("\n按 Enter 继续...")
    
    test_similarity_comparison(vsm)
    input("\n按 Enter 继续...")
    
    test_boolean_vs_ranked(ranked_retrieval)
    input("\n按 Enter 继续...")
    
    test_different_tf_schemes(inverted_posting_lists)
    input("\n按 Enter 继续...")
    
    test_performance_analysis(vsm)
    input("\n按 Enter 继续...")
    
    analyze_results_quality(vsm)
    
    # 总结
    print("\n\n" + "="*100)
    print(" "*40 + "测试完成!")
    print("="*100)
#     print("""
# 测试总结:
#   ✓ TF-IDF计算 - 验证权重计算正确性
#   ✓ 文档向量 - 稀疏向量表示和归一化
#   ✓ 排名检索 - 基于余弦相似度的文档排序
#   ✓ 查询扩展 - 查询长度对结果的影响
#   ✓ 文档相似度 - 同主题文档相似度更高
#   ✓ 模式对比 - 布尔检索vs排名检索
#   ✓ TF方案对比 - 不同计算方案的效果
#   ✓ 性能分析 - 查询响应时间
#   ✓ 结果质量 - 精确率和召回率

# 关键发现:
#   • TF-IDF有效区分重要词项和常见词项
#   • 余弦相似度能准确衡量文档相关性
#   • 同主题文档相似度显著高于不同主题
#   • 排名检索提供了比布尔检索更好的用户体验
#   • log TF方案通常比raw TF效果更好

# 应用场景:
#   • 文档排名和推荐
#   • 相似文档查找
#   • 主题分类和聚类
#   • 信息过滤
#   • 个性化搜索
#     """)
    print("="*100 + "\n")


if __name__ == "__main__":
    main()