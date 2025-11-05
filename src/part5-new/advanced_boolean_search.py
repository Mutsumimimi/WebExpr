"""
增强版布尔检索引擎
支持详细的性能监控和操作计数
"""

import time
from collections import defaultdict


class AdvancedBooleanSearchEngine:
    """
    带性能监控的布尔检索引擎
    记录每次操作的细节，用于分析优化效果
    """
    
    def __init__(self, dictionary_index, inverted_posting_lists):
        self.dictionary = dictionary_index
        self.posting_lists = inverted_posting_lists
        self.reset_metrics()
    
    def reset_metrics(self):
        """重置性能指标"""
        self.metrics = {
            'posting_list_accesses': 0,      # posting list访问次数
            'set_operations': 0,              # 集合操作次数
            'comparison_count': 0,            # 比较操作次数
            'intermediate_result_sizes': [],  # 中间结果集大小
            'operation_times': [],            # 每个操作的时间
            'operation_sequence': []          # 操作序列
        }
    
    def get_posting_list(self, token):
        """获取posting list并记录访问"""
        self.metrics['posting_list_accesses'] += 1
        
        if token not in self.posting_lists:
            return set()
        
        start_time = time.perf_counter()
        skip_list = self.posting_lists[token]
        doc_ids = set()
        
        current = skip_list.header.forward[0]
        while current:
            doc_ids.add(current.value.id)
            self.metrics['comparison_count'] += 1
            current = current.forward[0]
        
        end_time = time.perf_counter()
        
        self.metrics['operation_times'].append({
            'operation': 'get_posting_list',
            'token': token,
            'size': len(doc_ids),
            'time': (end_time - start_time) * 1000
        })
        
        return doc_ids
    
    def boolean_and(self, posting1, posting2, label="AND"):
        """AND操作 - 带性能监控"""
        self.metrics['set_operations'] += 1
        
        start_time = time.perf_counter()
        
        # 使用较小的集合进行迭代（优化）
        if len(posting1) > len(posting2):
            posting1, posting2 = posting2, posting1
        
        result = set()
        for doc_id in posting1:
            self.metrics['comparison_count'] += 1
            if doc_id in posting2:
                result.add(doc_id)
        
        end_time = time.perf_counter()
        
        self.metrics['intermediate_result_sizes'].append(len(result))
        self.metrics['operation_times'].append({
            'operation': label,
            'input_sizes': (len(posting1), len(posting2)),
            'output_size': len(result),
            'time': (end_time - start_time) * 1000,
            'comparisons': len(posting1)
        })
        self.metrics['operation_sequence'].append({
            'op': label,
            'input1_size': len(posting1),
            'input2_size': len(posting2),
            'output_size': len(result)
        })
        
        return result
    
    def boolean_or(self, posting1, posting2, label="OR"):
        """OR操作 - 带性能监控"""
        self.metrics['set_operations'] += 1
        
        start_time = time.perf_counter()
        result = posting1 | posting2
        end_time = time.perf_counter()
        
        self.metrics['intermediate_result_sizes'].append(len(result))
        self.metrics['operation_times'].append({
            'operation': label,
            'input_sizes': (len(posting1), len(posting2)),
            'output_size': len(result),
            'time': (end_time - start_time) * 1000
        })
        self.metrics['operation_sequence'].append({
            'op': label,
            'input1_size': len(posting1),
            'input2_size': len(posting2),
            'output_size': len(result)
        })
        
        return result
    
    def boolean_not(self, posting1, all_docs, label="NOT"):
        """NOT操作 - 带性能监控"""
        self.metrics['set_operations'] += 1
        
        start_time = time.perf_counter()
        result = all_docs - posting1
        end_time = time.perf_counter()
        
        self.metrics['intermediate_result_sizes'].append(len(result))
        self.metrics['operation_times'].append({
            'operation': label,
            'input_size': len(posting1),
            'output_size': len(result),
            'time': (end_time - start_time) * 1000
        })
        self.metrics['operation_sequence'].append({
            'op': label,
            'input_size': len(posting1),
            'output_size': len(result)
        })
        
        return result
    
    def get_all_documents(self):
        """获取所有文档ID集合"""
        all_docs = set()
        for skip_list in self.posting_lists.values():
            current = skip_list.header.forward[0]
            while current:
                all_docs.add(current.value.id)
                current = current.forward[0]
        return all_docs
    
    def tokenize_query(self, query):
        """分词"""
        query = query.replace('(', ' ( ').replace(')', ' ) ')
        tokens = query.split()
        return tokens
    
    def parse_expression(self, tokens):
        """解析表达式 - 带详细监控"""
        def find_matching_paren(tokens, start):
            count = 1
            for i in range(start + 1, len(tokens)):
                if tokens[i] == '(':
                    count += 1
                elif tokens[i] == ')':
                    count -= 1
                    if count == 0:
                        return i
            return -1
        
        result = None
        operation = None
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token == '(':
                end = find_matching_paren(tokens, i)
                if end == -1:
                    raise ValueError("括号不匹配")
                sub_result = self.parse_expression(tokens[i+1:end])
                
                if result is None:
                    result = sub_result
                elif operation == 'AND':
                    result = self.boolean_and(result, sub_result, f"AND_level_{i}")
                elif operation == 'OR':
                    result = self.boolean_or(result, sub_result, f"OR_level_{i}")
                
                i = end + 1
                
            elif token in ['AND', 'OR']:
                operation = token
                i += 1
                
            elif token == 'NOT':
                i += 1
                if i >= len(tokens):
                    raise ValueError("NOT操作符后缺少操作数")
                
                next_token = tokens[i]
                if next_token == '(':
                    end = find_matching_paren(tokens, i)
                    if end == -1:
                        raise ValueError("括号不匹配")
                    sub_result = self.parse_expression(tokens[i+1:end])
                    i = end + 1
                else:
                    sub_result = self.get_posting_list(next_token)
                    i += 1
                
                all_docs = self.get_all_documents()
                not_result = self.boolean_not(sub_result, all_docs, f"NOT_{next_token}")
                
                if result is None:
                    result = not_result
                elif operation == 'AND':
                    result = self.boolean_and(result, not_result, f"AND_NOT_{i}")
                elif operation == 'OR':
                    result = self.boolean_or(result, not_result, f"OR_NOT_{i}")
                    
            elif token != ')':
                current_posting = self.get_posting_list(token)
                
                if result is None:
                    result = current_posting
                elif operation == 'AND':
                    result = self.boolean_and(result, current_posting, f"AND_{token}")
                elif operation == 'OR':
                    result = self.boolean_or(result, current_posting, f"OR_{token}")
                
                i += 1
            else:
                i += 1
        
        return result if result is not None else set()
    
    def search(self, query):
        """执行查询"""
        self.reset_metrics()
        tokens = self.tokenize_query(query)
        result = self.parse_expression(tokens)
        return result
    
    def get_metrics_summary(self):
        """获取性能指标摘要"""
        total_time = sum(op['time'] for op in self.metrics['operation_times'])
        
        return {
            'total_time_ms': total_time,
            'posting_accesses': self.metrics['posting_list_accesses'],
            'set_operations': self.metrics['set_operations'],
            'comparisons': self.metrics['comparison_count'],
            'max_intermediate_size': max(self.metrics['intermediate_result_sizes']) if self.metrics['intermediate_result_sizes'] else 0,
            'avg_intermediate_size': sum(self.metrics['intermediate_result_sizes']) / len(self.metrics['intermediate_result_sizes']) if self.metrics['intermediate_result_sizes'] else 0,
            'operation_sequence': self.metrics['operation_sequence']
        }
    
    def print_detailed_metrics(self):
        """打印详细的性能指标"""
        print("\n【详细性能指标】")
        print("-"*100)
        
        print(f"Posting List 访问次数: {self.metrics['posting_list_accesses']}")
        print(f"集合操作次数: {self.metrics['set_operations']}")
        print(f"比较操作次数: {self.metrics['comparison_count']}")
        
        if self.metrics['intermediate_result_sizes']:
            print(f"最大中间结果集: {max(self.metrics['intermediate_result_sizes'])} 个文档")
            print(f"平均中间结果集: {sum(self.metrics['intermediate_result_sizes']) / len(self.metrics['intermediate_result_sizes']):.1f} 个文档")
        
        print("\n【操作序列】")
        print(f"{'操作':<20} {'输入大小':<30} {'输出大小':<15} {'耗时(ms)':<15}")
        print("-"*100)
        
        for op in self.metrics['operation_times']:
            if op['operation'] == 'get_posting_list':
                print(f"{op['operation']:<20} Token: {op['token']:<20} {op['size']:<15} {op['time']:.4f}")
            else:
                input_info = f"{op.get('input_sizes', 'N/A')}"
                print(f"{op['operation']:<20} {input_info:<30} {op['output_size']:<15} {op['time']:.4f}")
        
        total_time = sum(op['time'] for op in self.metrics['operation_times'])
        print("-"*100)
        print(f"{'总计':<20} {'':<30} {'':<15} {total_time:.4f}")


def compare_query_orders_detailed(search_engine, queries_with_orders):
    """
    详细比较不同处理顺序的性能
    
    :param search_engine: AdvancedBooleanSearchEngine实例
    :param queries_with_orders: [(query, description), ...]
    """
    print("\n" + "="*100)
    print("详细的处理顺序对比分析")
    print("="*100)
    
    results = []
    
    for query, description in queries_with_orders:
        print(f"\n{'-'*100}")
        print(f"查询: {query}")
        print(f"描述: {description}")
        print(f"{'-'*100}")
        
        # 执行查询
        result = search_engine.search(query)
        metrics = search_engine.get_metrics_summary()
        
        print(f"\n结果集大小: {len(result)} 个文档")
        print(f"总耗时: {metrics['total_time_ms']:.4f} ms")
        print(f"Posting List访问: {metrics['posting_accesses']} 次")
        print(f"比较操作: {metrics['comparisons']} 次")
        print(f"最大中间结果: {metrics['max_intermediate_size']} 个文档")
        
        # 打印操作序列
        print(f"\n操作执行顺序:")
        for i, op in enumerate(metrics['operation_sequence'], 1):
            if op['op'] in ['AND', 'OR']:
                print(f"  {i}. {op['op']}: ({op['input1_size']}, {op['input2_size']}) -> {op['output_size']}")
            else:
                print(f"  {i}. {op['op']}: {op.get('input_size', 'N/A')} -> {op['output_size']}")
        
        results.append({
            'query': query,
            'description': description,
            'time': metrics['total_time_ms'],
            'comparisons': metrics['comparisons'],
            'result_size': len(result)
        })
    
    # 对比总结
    print(f"\n\n{'='*100}")
    print("性能对比总结")
    print(f"{'='*100}")
    print(f"{'描述':<40} {'查询':<35} {'耗时(ms)':<15} {'比较次数':<15}")
    print("-"*100)
    
    for r in results:
        print(f"{r['description']:<40} {r['query']:<35} {r['time']:>8.4f}      {r['comparisons']:>10}")
    
    if len(results) > 1:
        fastest = min(results, key=lambda x: x['time'])
        slowest = max(results, key=lambda x: x['time'])
        print(f"\n最快: {fastest['description']} ({fastest['time']:.4f} ms)")
        print(f"最慢: {slowest['description']} ({slowest['time']:.4f} ms)")
        print(f"性能差异: {slowest['time'] / fastest['time']:.2f}x")


def analyze_and_operation_cost(search_engine, token_pairs):
    """
    分析AND操作的实际计算成本
    
    :param search_engine: 检索引擎实例
    :param token_pairs: [(token1, token2, expected_behavior), ...]
    """
    print("\n" + "="*100)
    print("AND操作成本分析")
    print("="*100)
    
    print(f"\n{'词项对':<40} {'顺序':<20} {'比较次数':<15} {'耗时(ms)':<15}")
    print("-"*100)
    
    for token1, token2, desc in token_pairs:
        # 测试两种顺序
        for order in [f"{token1} AND {token2}", f"{token2} AND {token1}"]:
            result = search_engine.search(order)
            metrics = search_engine.get_metrics_summary()
            
            print(f"{desc:<40} {order:<20} {metrics['comparisons']:<15} {metrics['total_time_ms']:>8.4f}")
    
    print("-"*100)
