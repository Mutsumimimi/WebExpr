'''
zyf: 这个暂时没用
'''

"""
布尔检索测试脚本
演示各种复杂查询场景
"""

import skiplist
import boolean_search

def create_test_data():
    """
    创建测试数据集
    返回: inverted_posting_lists, dictionary_index
    """
    # 模拟文档集合
    test_documents = {
        "doc1": {"apple": [0, 5, 10], "banana": [2, 7]},
        "doc2": {"apple": [1], "cherry": [3, 8]},
        "doc3": {"banana": [0], "cherry": [4], "date": [9]},
        "doc4": {"apple": [2], "banana": [6], "date": [11]},
        "doc5": {"cherry": [1, 5], "date": [8]},
        "doc6": {"apple": [0], "banana": [3], "cherry": [7]},
        "doc7": {"elderberry": [2], "fig": [5]},
        "doc8": {"apple": [1], "elderberry": [4], "grape": [9]}
    }
    
    # 构建倒排索引
    inverted_posting_lists = {}
    MAX_LEVEL = 16
    P = 0.5
    
    # 收集所有唯一token
    all_tokens = set()
    for doc_tokens in test_documents.values():
        all_tokens.update(doc_tokens.keys())
    
    # 为每个token创建SkipList
    for token in all_tokens:
        skip_list = skiplist.SkipList(max_level=MAX_LEVEL, p=P)
        
        # 遍历所有文档，插入包含该token的文档
        for doc_id, doc_tokens in test_documents.items():
            if token in doc_tokens:
                positions = doc_tokens[token]
                posting = skiplist.Value(doc_id, positions)
                skip_list.insert(posting)
        
        inverted_posting_lists[token] = skip_list
    
    # 创建简化的词典索引（仅用于测试）
    dictionary_index = {}
    for i, token in enumerate(sorted(all_tokens)):
        entry = skiplist.DictionaryEntry(
            block_id=i // 4,
            term_string_offset=i * 10,
            compressed_length=10,
            df=len([d for d in test_documents if token in test_documents[d]]),
            post_list_ref=inverted_posting_lists[token]
        )
        dictionary_index[token] = entry
    
    return inverted_posting_lists, dictionary_index, test_documents


def print_test_data_info(test_documents, inverted_posting_lists):
    """打印测试数据信息"""
    print("="*80)
    print("测试数据集信息")
    print("="*80)
    
    print("\n【文档内容】")
    for doc_id, tokens in sorted(test_documents.items()):
        token_list = ", ".join([f"{t}@{pos}" for t, positions in tokens.items() 
                                for pos in positions])
        print(f"{doc_id}: {token_list}")
    
    print("\n【倒排索引】")
    for token in sorted(inverted_posting_lists.keys()):
        skip_list = inverted_posting_lists[token]
        doc_ids = []
        current = skip_list.header.forward[0]
        while current:
            doc_ids.append(current.value.id)
            current = current.forward[0]
        print(f"{token:12s} -> {sorted(doc_ids)}")


def run_comprehensive_tests(search_engine):
    """运行全面的测试用例"""
    print("\n\n")
    print("="*80)
    print("全面测试 - 10种查询场景")
    print("="*80)
    
    test_cases = [
        # 基础查询
        ("单词查询", "apple"),
        ("AND查询", "apple AND banana"),
        ("OR查询", "apple OR cherry"),
        
        # NOT操作
        ("NOT查询", "NOT date"),
        ("AND NOT组合", "apple AND NOT cherry"),
        ("OR NOT组合", "banana OR NOT date"),
        
        # 复杂括号
        ("简单括号", "(apple OR banana) AND cherry"),
        ("嵌套括号", "(apple AND banana) OR (cherry AND date)"),
        ("多层嵌套", "((apple OR banana) AND cherry) OR elderberry"),
        
        # 复杂组合
        ("复杂组合1", "(apple AND banana) AND NOT (cherry OR date)"),
    ]
    
    for i, (name, query) in enumerate(test_cases, 1):
        print(f"\n【测试{i}】{name}")
        print(f"查询: {query}")
        try:
            result = search_engine.search(query)
            print(f"结果: {sorted(result) if result else '∅ (空集)'}")
            print(f"文档数: {len(result)}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def test_edge_cases(search_engine):
    """测试边界情况"""
    print("\n\n")
    print("="*80)
    print("边界情况测试")
    print("="*80)
    
    edge_cases = [
        ("空查询", "nonexistent"),
        ("多个NOT", "NOT apple AND NOT banana"),
        ("只有NOT", "NOT apple"),
        ("嵌套NOT", "NOT (apple OR banana)"),
        ("复杂空集", "apple AND banana AND cherry AND date AND elderberry"),
    ]
    
    for i, (name, query) in enumerate(edge_cases, 1):
        print(f"\n【边界{i}】{name}")
        print(f"查询: {query}")
        try:
            result = search_engine.search(query)
            print(f"结果: {sorted(result) if result else '∅ (空集)'}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def test_position_retrieval(search_engine):
    """测试位置检索功能"""
    print("\n\n")
    print("="*80)
    print("位置检索测试")
    print("="*80)
    
    tokens = ["apple", "banana", "cherry"]
    
    for token in tokens:
        print(f"\n【Token: {token}】")
        positions = search_engine.search_with_positions(token)
        
        if not positions:
            print("  未找到该词项")
        else:
            for doc_id, pos_list in sorted(positions.items()):
                print(f"  {doc_id}: 位置 {pos_list}")


def compare_query_efficiency(search_engine):
    """比较不同查询的效率"""
    print("\n\n")
    print("="*80)
    print("查询效率对比")
    print("="*80)
    
    queries = [
        ("简单AND", "apple AND banana"),
        ("简单OR", "apple OR banana"),
        ("复杂表达式", "(apple OR banana) AND (cherry OR date)"),
    ]
    
    for name, query in queries:
        print(f"\n【{name}】{query}")
        
        tokens = search_engine.tokenize_query(query)
        term_tokens = [t for t in tokens if t not in ['AND', 'OR', 'NOT', '(', ')']]
        
        print(f"  涉及词项: {term_tokens}")
        
        # 统计每个词项的posting list大小
        for token in term_tokens:
            postings = search_engine.get_posting_list(token)
            print(f"    {token}: {len(postings)} 个文档")
        
        result = search_engine.search(query)
        print(f"  最终结果: {len(result)} 个文档")
        print(f"  结果集: {sorted(result)}")


def main():
    """主测试函数"""
    print("布尔检索系统 - 综合测试")
    print("="*80)
    
    # 1. 创建测试数据
    inverted_posting_lists, dictionary_index, test_documents = create_test_data()
    
    # 2. 显示测试数据
    print_test_data_info(test_documents, inverted_posting_lists)
    
    # 3. 初始化检索引擎
    search_engine = boolean_search.BooleanSearchEngine(
        dictionary_index=dictionary_index,
        inverted_posting_lists=inverted_posting_lists
    )
    
    # 4. 运行各类测试
    run_comprehensive_tests(search_engine)
    test_edge_cases(search_engine)
    test_position_retrieval(search_engine)
    compare_query_efficiency(search_engine)
    
    print("\n\n" + "="*80)
    print("✓ 所有测试完成")
    print("="*80)


if __name__ == "__main__":
    main()