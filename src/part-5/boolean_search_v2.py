"""
布尔检索模块 - 支持复杂查询表达式和短语查询
支持的操作符:
1. AND - 交集操作
2. OR - 并集操作  
3. NOT - 差集操作
4. 括号 () - 控制优先级
5. 短语查询 "phrase" - 精确匹配短语（词项按顺序相邻）
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
    
    def get_posting_list_with_positions(self, token):
        """
        获取token的posting list（包含位置信息）
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
    
    def phrase_query(self, phrase_tokens):
        """
        短语查询 - 查找包含指定短语的文档
        :param phrase_tokens: 短语中的词项列表，如 ["information", "retrieval"]
        :return: set of doc_ids
        """
        if not phrase_tokens:
            return set()
        
        if len(phrase_tokens) == 1:
            # 单个词项，直接返回posting list
            return self.get_posting_list(phrase_tokens[0])
        
        # 1. 获取第一个词项的posting list（带位置）
        first_token = phrase_tokens[0]
        first_positions = self.get_posting_list_with_positions(first_token)
        
        # 候选文档集合（包含所有词项的文档）
        candidate_docs = set(first_positions.keys())
        
        # 2. 对于短语中的其他词项，计算交集
        for i in range(1, len(phrase_tokens)):
            token = phrase_tokens[i]
            token_positions = self.get_posting_list_with_positions(token)
            
            # 只保留同时包含当前词项的文档
            candidate_docs = candidate_docs & set(token_positions.keys())
            
            if not candidate_docs:
                return set()
        
        # 3. 获取所有词项的位置信息
        all_positions = []
        for token in phrase_tokens:
            all_positions.append(self.get_posting_list_with_positions(token))
        
        # 4. 位置验证：检查词项是否在文档中按顺序相邻出现
        result_docs = set()
        
        for doc_id in candidate_docs:
            if self._verify_phrase_positions(doc_id, phrase_tokens, all_positions):
                result_docs.add(doc_id)
        
        return result_docs
    
    def _verify_phrase_positions(self, doc_id, phrase_tokens, all_positions):
        """
        验证短语中的词项是否在文档中按顺序相邻出现
        :param doc_id: 文档ID
        :param phrase_tokens: 短语词项列表
        :param all_positions: 每个词项的位置信息列表
        :return: True if 短语匹配，False otherwise
        """
        # 获取第一个词项在该文档中的所有位置
        first_token_positions = all_positions[0].get(doc_id, [])
        
        # 对于第一个词项的每个位置，检查后续词项是否按顺序相邻
        for start_pos in first_token_positions:
            match = True
            
            # 检查短语中的每个后续词项
            for i in range(1, len(phrase_tokens)):
                expected_pos = start_pos + i
                token_positions = all_positions[i].get(doc_id, [])
                
                # 检查期望位置是否在词项的位置列表中
                if expected_pos not in token_positions:
                    match = False
                    break
            
            # 如果找到完整匹配，返回True
            if match:
                return True
        
        return False
    
    def positional_intersect(self, term1, term2, k=1):
        """
        位置感知的交集操作（邻近查询）
        :param term1: 第一个词项
        :param term2: 第二个词项
        :param k: 词项间的最大距离，k=1表示相邻
        :return: {doc_id: [(pos1, pos2), ...]} - 满足邻近条件的位置对
        """
        pos1 = self.get_posting_list_with_positions(term1)
        pos2 = self.get_posting_list_with_positions(term2)
        
        # 找到同时包含两个词项的文档
        common_docs = set(pos1.keys()) & set(pos2.keys())
        
        result = {}
        
        for doc_id in common_docs:
            positions1 = pos1[doc_id]
            positions2 = pos2[doc_id]
            
            # 找出满足距离要求的位置对
            valid_pairs = []
            for p1 in positions1:
                for p2 in positions2:
                    # 检查term2是否在term1后面，且距离在k以内
                    if 0 < p2 - p1 <= k:
                        valid_pairs.append((p1, p2))
            
            if valid_pairs:
                result[doc_id] = valid_pairs
        
        return result
    
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
        将查询字符串分词，支持短语查询（用引号括起来）
        :param query: 查询表达式，如 "apple AND \"information retrieval\""
        :return: token列表
        """
        tokens = []
        current_token = ""
        in_phrase = False
        phrase_content = ""
        
        i = 0
        while i < len(query):
            char = query[i]
            
            if char == '"':
                if in_phrase:
                    # 短语结束
                    tokens.append(f'PHRASE:{phrase_content.strip()}')
                    phrase_content = ""
                    in_phrase = False
                else:
                    # 短语开始
                    if current_token.strip():
                        tokens.append(current_token.strip())
                        current_token = ""
                    in_phrase = True
                i += 1
                continue
            
            if in_phrase:
                phrase_content += char
                i += 1
                continue
            
            if char in '()':
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
                tokens.append(char)
            elif char.isspace():
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
            else:
                current_token += char
            
            i += 1
        
        # 处理最后一个token
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens
    
    def parse_expression(self, tokens):
        """
        递归解析布尔表达式（支持短语查询）
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
                elif next_token.startswith('PHRASE:'):
                    # 短语查询
                    phrase_content = next_token[7:]  # 去掉 'PHRASE:' 前缀
                    phrase_tokens = phrase_content.split()
                    sub_result = self.phrase_query(phrase_tokens)
                    i += 1
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
                # 检查是否是短语查询
                if token.startswith('PHRASE:'):
                    phrase_content = token[7:]  # 去掉 'PHRASE:' 前缀
                    phrase_tokens = phrase_content.split()
                    current_posting = self.phrase_query(phrase_tokens)
                else:
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
        执行布尔检索（支持短语查询）
        :param query: 布尔查询表达式，支持短语用引号括起来
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
        return self.get_posting_list_with_positions(token)
    
    def search_phrase_with_positions(self, phrase_tokens):
        """
        短语查询并返回匹配位置
        :param phrase_tokens: 短语词项列表
        :return: {doc_id: [start_positions]} - 短语在文档中的起始位置
        """
        if not phrase_tokens:
            return {}
        
        if len(phrase_tokens) == 1:
            return self.get_posting_list_with_positions(phrase_tokens[0])
        
        # 获取所有词项的位置信息
        all_positions = []
        candidate_docs = None
        
        for token in phrase_tokens:
            token_positions = self.get_posting_list_with_positions(token)
            all_positions.append(token_positions)
            
            if candidate_docs is None:
                candidate_docs = set(token_positions.keys())
            else:
                candidate_docs = candidate_docs & set(token_positions.keys())
        
        # 找出短语的起始位置
        result = {}
        
        for doc_id in candidate_docs:
            start_positions = []
            first_token_positions = all_positions[0].get(doc_id, [])
            
            for start_pos in first_token_positions:
                match = True
                
                for i in range(1, len(phrase_tokens)):
                    expected_pos = start_pos + i
                    token_positions = all_positions[i].get(doc_id, [])
                    
                    if expected_pos not in token_positions:
                        match = False
                        break
                
                if match:
                    start_positions.append(start_pos)
            
            if start_positions:
                result[doc_id] = start_positions
        
        return result


# --- 示例查询函数 ---

def demo_phrase_search(search_engine):
    """
    演示短语查询功能
    """
    print("\n" + "="*80)
    print("短语查询演示")
    print("="*80)
    
    # 示例1: 简单短语查询
    query1 = '"last week"'
    print(f"\n【查询1】简单短语: {query1}")
    try:
        result1 = search_engine.search(query1)
        print(f"结果: {sorted(result1) if result1 else '无匹配文档'}")
        print(f"匹配文档数: {len(result1)}")
        
        # 显示匹配位置
        phrase_tokens = ["last", "week"]
        positions = search_engine.search_phrase_with_positions(phrase_tokens)
        if positions:
            print(f"\n匹配位置:")
            for doc_id, pos_list in sorted(positions.items()):
                print(f"  文档 {doc_id}: 位置 {pos_list}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例2: 短语查询与布尔操作结合
    query2 = '"last week" AND tea'
    print(f"\n【查询2】短语+AND: {query2}")
    try:
        result2 = search_engine.search(query2)
        print(f"结果: {sorted(result2) if result2 else '无匹配文档'}")
        print(f"匹配文档数: {len(result2)}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例3: 多个短语的OR操作
    query3 = '"food water" OR "around world"'
    print(f"\n【查询3】短语OR短语: {query3}")
    try:
        result3 = search_engine.search(query3)
        print(f"结果: {sorted(result3) if result3 else '无匹配文档'}")
        print(f"匹配文档数: {len(result3)}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例4: NOT短语查询
    query4 = 'system AND NOT "information retrieval"'
    print(f"\n【查询4】AND NOT 短语: {query4}")
    try:
        result4 = search_engine.search(query4)
        print(f"结果: {sorted(result4) if result4 else '无匹配文档'}")
        print(f"匹配文档数: {len(result4)}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例5: 复杂嵌套查询
    query5 = '(appl AND banana) OR "cherry date"'
    print(f"\n【查询5】复杂嵌套: {query5}")
    try:
        result5 = search_engine.search(query5)
        print(f"结果: {sorted(result5) if result5 else '无匹配文档'}")
        print(f"匹配文档数: {len(result5)}")
    except Exception as e:
        print(f"查询出错: {e}")


def demo_proximity_search(search_engine):
    """
    演示邻近查询功能
    """
    print("\n" + "="*80)
    print("邻近查询演示")
    print("="*80)
    
    # 示例：查找"information"和"retrieval"在文档中距离不超过3个词的情况
    print(f"\n【邻近查询】information 和 retrieval 距离 ≤ 3")
    
    result = search_engine.positional_intersect("information", "retrieval", k=3)
    
    if result:
        print(f"找到 {len(result)} 个匹配文档:")
        for doc_id, positions in sorted(result.items()):
            print(f"  文档 {doc_id}:")
            for p1, p2 in positions:
                print(f"    位置对: ({p1}, {p2}), 距离: {p2 - p1}")
    else:
        print("无匹配文档")


def demo_boolean_search(search_engine):
    """
    演示基础布尔查询（原有功能）
    """
    print("\n" + "="*80)
    print("布尔检索演示 - 三种复杂查询")
    print("="*80)
    
    # 查询1: AND操作
    query1 = "appl AND banana"
    print(f"\n【查询1】AND操作: {query1}")
    result1 = search_engine.search(query1)
    print(f"结果: {sorted(result1) if result1 else '无匹配文档'}")
    print(f"匹配文档数: {len(result1)}")
    
    # 查询2: OR + NOT操作
    query2 = "(appl OR banana) AND NOT chat"
    print(f"\n【查询2】复合操作: {query2}")
    result2 = search_engine.search(query2)
    print(f"结果: {sorted(result2) if result2 else '无匹配文档'}")
    print(f"匹配文档数: {len(result2)}")
    
    # 查询3: 嵌套括号
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
                if token.startswith('PHRASE:'):
                    phrase_content = token[7:]
                    phrase_tokens = phrase_content.split()
                    # 短语的大小是所有词项posting list的交集大小
                    phrase_result = search_engine.phrase_query(phrase_tokens)
                    posting_sizes[token] = len(phrase_result)
                else:
                    posting_sizes[token] = len(search_engine.get_posting_list(token))
        
        print(f"\n查询{i}: {query}")
        print(f"涉及词项: {list(posting_sizes.keys())}")
        print(f"Posting List大小: {posting_sizes}")
        
        result = search_engine.search(query)
        print(f"最终结果集大小: {len(result)}")