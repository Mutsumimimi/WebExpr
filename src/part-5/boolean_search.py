"""
布尔检索模块 - 支持复杂查询表达式
支持的操作符:
1. AND - 交集操作
2. OR - 并集操作  
3. NOT - 差集操作
4. 括号 () - 控制优先级
"""

class BooleanSearchEngine:
    def __init__(self, dictionary_index, inverted_posting_lists):
        """
        初始化布尔检索引擎
        :param dictionary_index: 压缩词典 {token: DictionaryEntry}
        :param inverted_posting_lists: 倒排索引 {token: SkipList}
        """
        self.dictionary = dictionary_index
        self.posting_lists = inverted_posting_lists
        
    def get_posting_list(self, token):
        """
        获取token的posting list（文档ID集合）
        :param token: 查询词项
        :return: set of doc_ids
        """
        if token not in self.posting_lists:
            return set()
        
        skip_list = self.posting_lists[token]
        doc_ids = set()
        
        # 遍历SkipList获取所有文档ID
        current = skip_list.header.forward[0]
        while current:
            doc_ids.add(current.value.id)
            current = current.forward[0]
            
        return doc_ids
    
    def boolean_and(self, posting1, posting2):
        """AND操作 - 交集"""
        return posting1 & posting2
    
    def boolean_or(self, posting1, posting2):
        """OR操作 - 并集"""
        return posting1 | posting2
    
    def boolean_not(self, posting1, all_docs):
        """NOT操作 - 差集（全集减去posting1）"""
        return all_docs - posting1
    
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
        """
        将查询字符串分词
        :param query: 查询表达式，如 "apple AND (banana OR cherry)"
        :return: token列表
        """
        # 替换括号为带空格的形式，便于分割
        query = query.replace('(', ' ( ').replace(')', ' ) ')
        tokens = query.split()
        return tokens
    
    def parse_expression(self, tokens):
        """
        递归解析布尔表达式
        :param tokens: token列表
        :return: 文档ID集合
        """
        # 处理括号优先级
        def find_matching_paren(tokens, start):
            """找到匹配的右括号"""
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
                # 找到匹配的右括号，递归处理子表达式
                end = find_matching_paren(tokens, i)
                if end == -1:
                    raise ValueError("括号不匹配")
                sub_result = self.parse_expression(tokens[i+1:end])
                
                if result is None:
                    result = sub_result
                elif operation == 'AND':
                    result = self.boolean_and(result, sub_result)
                elif operation == 'OR':
                    result = self.boolean_or(result, sub_result)
                
                i = end + 1
                
            elif token in ['AND', 'OR']:
                operation = token
                i += 1
                
            elif token == 'NOT':
                # NOT操作符
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
                not_result = self.boolean_not(sub_result, all_docs)
                
                if result is None:
                    result = not_result
                elif operation == 'AND':
                    result = self.boolean_and(result, not_result)
                elif operation == 'OR':
                    result = self.boolean_or(result, not_result)
                    
            elif token != ')':
                # 普通词项
                current_posting = self.get_posting_list(token)
                
                if result is None:
                    result = current_posting
                elif operation == 'AND':
                    result = self.boolean_and(result, current_posting)
                elif operation == 'OR':
                    result = self.boolean_or(result, current_posting)
                
                i += 1
            else:
                i += 1
        
        return result if result is not None else set()
    
    def search(self, query):
        """
        执行布尔检索
        :param query: 布尔查询表达式
        :return: 匹配的文档ID集合
        """
        tokens = self.tokenize_query(query)
        result = self.parse_expression(tokens)
        return result
    
    def search_with_positions(self, token):
        """
        获取token在文档中的详细位置信息
        :param token: 查询词项
        :return: {doc_id: [positions]}
        """
        if token not in self.posting_lists:
            return {}
        
        skip_list = self.posting_lists[token]
        positions = {}
        
        current = skip_list.header.forward[0]
        while current:
            doc_id = current.value.id
            pos_list = current.value.pos
            positions[doc_id] = pos_list
            current = current.forward[0]
            
        return positions


# --- 示例查询函数 ---

def demo_boolean_search(search_engine):
    """
    演示三种复杂查询
    """
    print("\n" + "="*80)
    print("布尔检索演示 - 三种复杂查询")
    print("="*80)
    
    # 查询1: AND操作 - 同时包含两个词的文档
    query1 = "appl AND banana"
    print(f"\n【查询1】AND操作: {query1}")
    result1 = search_engine.search(query1)
    print(f"结果: {sorted(result1) if result1 else '无匹配文档'}")
    print(f"匹配文档数: {len(result1)}")
    
    # 查询2: OR + NOT操作 - 包含A或B，但不包含C
    query2 = "(appl OR banana) AND NOT chat"
    print(f"\n【查询2】复合操作: {query2}")
    result2 = search_engine.search(query2)
    print(f"结果: {sorted(result2) if result2 else '无匹配文档'}")
    print(f"匹配文档数: {len(result2)}")
    
    # 查询3: 嵌套括号 - 复杂优先级
    query3 = "(appl AND NOT banana) OR (chat AND date)"
    print(f"\n【查询3】嵌套表达式: {query3}")
    result3 = search_engine.search(query3)
    print(f"结果: {sorted(result3) if result3 else '无匹配文档'}")
    print(f"匹配文档数: {len(result3)}")
    
    query4 = "chat AND date"
    print(f"\n【查询1】AND操作: {query4}")
    result4 = search_engine.search(query4)
    print(f"结果: {sorted(result4) if result4 else '无匹配文档'}")
    print(f"匹配文档数: {len(result4)}")
    
    # 附加：显示详细位置信息
    print("\n" + "-"*80)
    print("详细位置信息示例 - token 'appl'")
    print("-"*80)
    positions = search_engine.search_with_positions('appl')
    for doc_id, pos_list in sorted(positions.items()):
        print(f"文档 {doc_id}: 出现位置 {pos_list}")
    
    return result1, result2, result3


# --- 性能统计 ---

def analyze_query_performance(search_engine, queries):
    """
    分析查询性能
    :param search_engine: 检索引擎实例
    :param queries: 查询列表
    """
    print("\n" + "="*80)
    print("查询性能分析")
    print("="*80)
    
    for i, query in enumerate(queries, 1):
        tokens = search_engine.tokenize_query(query)
        
        # 统计每个token的posting list大小
        posting_sizes = {}
        for token in tokens:
            if token not in ['AND', 'OR', 'NOT', '(', ')']:
                posting_sizes[token] = len(search_engine.get_posting_list(token))
        
        print(f"\n查询{i}: {query}")
        print(f"涉及词项: {list(posting_sizes.keys())}")
        print(f"Posting List大小: {posting_sizes}")
        
        result = search_engine.search(query)
        print(f"最终结果集大小: {len(result)}")