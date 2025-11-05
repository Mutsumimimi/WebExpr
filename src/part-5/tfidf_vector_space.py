"""
TF-IDF 与向量空间模型实现
支持排名检索和相似度计算
"""

import math
from collections import defaultdict
import heapq


class TFIDFCalculator:
    """TF-IDF计算器"""
    
    def __init__(self, tf_scheme='log', idf_scheme='standard'):
        """
        :param tf_scheme: TF计算方案 ('raw', 'log', 'boolean', 'augmented')
        :param idf_scheme: IDF计算方案 ('standard', 'smooth', 'probabilistic')
        """
        self.tf_scheme = tf_scheme
        self.idf_scheme = idf_scheme
    
    def compute_tf(self, term_count, doc_length=None, max_count=None):
        """
        计算词项频率 (TF)
        :param term_count: 词项在文档中出现的次数
        :param doc_length: 文档总词数（用于归一化）
        :param max_count: 文档中出现最多的词项的次数
        :return: TF值
        """
        if self.tf_scheme == 'raw':
            return term_count
        elif self.tf_scheme == 'log':
            return 1 + math.log10(term_count) if term_count > 0 else 0
        elif self.tf_scheme == 'boolean':
            return 1 if term_count > 0 else 0
        elif self.tf_scheme == 'augmented':
            if max_count and max_count > 0:
                return 0.5 + 0.5 * (term_count / max_count)
            return term_count
        else:
            return term_count
    
    def compute_idf(self, num_docs, doc_freq):
        """
        计算逆文档频率 (IDF)
        :param num_docs: 文档总数
        :param doc_freq: 包含该词项的文档数
        :return: IDF值
        """
        if doc_freq == 0:
            return 0
        
        if self.idf_scheme == 'standard':
            return math.log10(num_docs / doc_freq)
        elif self.idf_scheme == 'smooth':
            return math.log10((num_docs + 1) / (doc_freq + 1)) + 1
        elif self.idf_scheme == 'probabilistic':
            if doc_freq >= num_docs:
                return 0
            return math.log10((num_docs - doc_freq) / doc_freq)
        else:
            return math.log10(num_docs / doc_freq)
    
    def compute_tfidf(self, tf, idf):
        """计算TF-IDF权重"""
        return tf * idf


class DocumentVector:
    """文档向量表示（稀疏向量）"""
    
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.weights = {}  # {term: weight}
        self.norm = 0.0    # 向量的L2范数
    
    def add_term(self, term, weight):
        """添加词项权重"""
        self.weights[term] = weight
    
    def normalize(self):
        """归一化向量（L2范数）"""
        sum_of_squares = sum(w ** 2 for w in self.weights.values())
        self.norm = math.sqrt(sum_of_squares)
        
        if self.norm > 0:
            for term in self.weights:
                self.weights[term] /= self.norm
    
    def dot_product(self, other_vector):
        """计算与另一个向量的点积"""
        result = 0.0
        # 只需遍历较小的向量
        smaller, larger = (self.weights, other_vector.weights) \
            if len(self.weights) < len(other_vector.weights) \
            else (other_vector.weights, self.weights)
        
        for term, weight in smaller.items():
            if term in larger:
                result += weight * larger[term]
        
        return result
    
    def cosine_similarity(self, other_vector):
        """计算余弦相似度"""
        if self.norm == 0 or other_vector.norm == 0:
            return 0.0
        
        dot_prod = self.dot_product(other_vector)
        return dot_prod / (self.norm * other_vector.norm)


class VectorSpaceModel:
    """向量空间模型"""
    
    def __init__(self, inverted_posting_lists, tf_scheme='log', idf_scheme='standard'):
        """
        :param inverted_posting_lists: 倒排索引 {term: SkipList}
        :param tf_scheme: TF计算方案
        :param idf_scheme: IDF计算方案
        """
        self.posting_lists = inverted_posting_lists
        self.calculator = TFIDFCalculator(tf_scheme, idf_scheme)
        
        # 统计信息
        self.num_docs = 0
        self.doc_lengths = {}     # {doc_id: length}
        self.df = {}              # {term: document_frequency}
        self.idf = {}             # {term: idf_value}
        self.doc_vectors = {}     # {doc_id: DocumentVector}
        
        # 构建模型
        self._build_model()
    
    def _build_model(self):
        """构建向量空间模型"""
        print("正在构建TF-IDF向量空间模型...")
        
        # 步骤1: 收集文档频率和文档长度
        self._collect_statistics()
        
        # 步骤2: 计算IDF
        self._compute_idf()
        
        # 步骤3: 构建文档向量
        self._build_document_vectors()
        
        print(f"✓ 模型构建完成: {self.num_docs} 个文档, {len(self.df)} 个词项")
    
    def _collect_statistics(self):
        """收集统计信息：DF和文档长度"""
        all_docs = set()
        term_doc_freq = defaultdict(int)
        doc_term_counts = defaultdict(lambda: defaultdict(int))
        
        # 遍历倒排索引
        for term, skip_list in self.posting_lists.items():
            current = skip_list.header.forward[0]
            
            while current:
                doc_id = current.value.id
                positions = current.value.pos
                
                all_docs.add(doc_id)
                term_doc_freq[term] += 1
                doc_term_counts[doc_id][term] = len(positions)
                
                current = current.forward[0]
        
        # 保存结果
        self.num_docs = len(all_docs)
        self.df = dict(term_doc_freq)
        
        # 计算文档长度
        for doc_id, term_counts in doc_term_counts.items():
            self.doc_lengths[doc_id] = sum(term_counts.values())
    
    def _compute_idf(self):
        """计算所有词项的IDF"""
        for term, doc_freq in self.df.items():
            self.idf[term] = self.calculator.compute_idf(self.num_docs, doc_freq)
    
    def _build_document_vectors(self):
        """构建所有文档的TF-IDF向量"""
        # 首先收集每个文档的词项频率
        doc_term_freqs = defaultdict(dict)
        
        for term, skip_list in self.posting_lists.items():
            current = skip_list.header.forward[0]
            
            while current:
                doc_id = current.value.id
                term_count = len(current.value.pos)
                doc_term_freqs[doc_id][term] = term_count
                current = current.forward[0]
        
        # 为每个文档构建向量
        for doc_id, term_freqs in doc_term_freqs.items():
            doc_vector = DocumentVector(doc_id)
            doc_length = self.doc_lengths[doc_id]
            max_count = max(term_freqs.values()) if term_freqs else 1
            
            for term, count in term_freqs.items():
                # 计算TF
                tf = self.calculator.compute_tf(count, doc_length, max_count)
                
                # 计算TF-IDF
                idf = self.idf.get(term, 0)
                tfidf = self.calculator.compute_tfidf(tf, idf)
                
                doc_vector.add_term(term, tfidf)
            
            # 归一化向量
            doc_vector.normalize()
            self.doc_vectors[doc_id] = doc_vector
    
    def build_query_vector(self, query_terms):
        """
        构建查询向量
        :param query_terms: 查询词项列表或字典 {term: count}
        :return: DocumentVector
        """
        # 处理输入
        if isinstance(query_terms, list):
            term_counts = defaultdict(int)
            for term in query_terms:
                term_counts[term] += 1
        else:
            term_counts = query_terms
        
        # 构建向量
        query_vector = DocumentVector("QUERY")
        max_count = max(term_counts.values()) if term_counts else 1
        query_length = sum(term_counts.values())
        
        for term, count in term_counts.items():
            # 计算TF
            tf = self.calculator.compute_tf(count, query_length, max_count)
            
            # 使用文档集合的IDF（查询中的新词IDF为0）
            idf = self.idf.get(term, 0)
            tfidf = self.calculator.compute_tfidf(tf, idf)
            
            if tfidf > 0:
                query_vector.add_term(term, tfidf)
        
        # 归一化
        query_vector.normalize()
        
        return query_vector
    
    def search(self, query_terms, top_k=10):
        """
        执行排名检索
        :param query_terms: 查询词项列表
        :param top_k: 返回前K个文档
        :return: [(doc_id, score), ...] 按得分降序排列
        """
        # 构建查询向量
        query_vector = self.build_query_vector(query_terms)
        
        # 获取候选文档（包含至少一个查询词的文档）
        candidate_docs = set()
        for term in query_terms:
            if term in self.posting_lists:
                skip_list = self.posting_lists[term]
                current = skip_list.header.forward[0]
                while current:
                    candidate_docs.add(current.value.id)
                    current = current.forward[0]
        
        # 计算相似度
        scores = []
        for doc_id in candidate_docs:
            doc_vector = self.doc_vectors.get(doc_id)
            if doc_vector:
                similarity = query_vector.cosine_similarity(doc_vector)
                if similarity > 0:
                    scores.append((doc_id, similarity))
        
        # 排序并返回Top-K
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def search_optimized(self, query_terms, top_k=10):
        """
        优化的排名检索（使用堆）
        :param query_terms: 查询词项列表
        :param top_k: 返回前K个文档
        :return: [(doc_id, score), ...] 按得分降序排列
        """
        query_vector = self.build_query_vector(query_terms)
        
        # 使用最小堆维护Top-K
        heap = []  # [(score, doc_id), ...]
        
        # 获取候选文档
        candidate_docs = set()
        for term in query_terms:
            if term in self.posting_lists:
                skip_list = self.posting_lists[term]
                current = skip_list.header.forward[0]
                while current:
                    candidate_docs.add(current.value.id)
                    current = current.forward[0]
        
        # 计算相似度并维护Top-K
        for doc_id in candidate_docs:
            doc_vector = self.doc_vectors.get(doc_id)
            if doc_vector:
                similarity = query_vector.cosine_similarity(doc_vector)
                
                if similarity > 0:
                    if len(heap) < top_k:
                        heapq.heappush(heap, (similarity, doc_id))
                    elif similarity > heap[0][0]:
                        heapq.heapreplace(heap, (similarity, doc_id))
        
        # 返回结果（降序）
        results = [(doc_id, score) for score, doc_id in sorted(heap, reverse=True)]
        return results
    
    def get_term_info(self, term):
        """获取词项信息"""
        return {
            'term': term,
            'document_frequency': self.df.get(term, 0),
            'idf': self.idf.get(term, 0),
            'exists': term in self.posting_lists
        }
    
    def get_document_info(self, doc_id):
        """获取文档信息"""
        doc_vector = self.doc_vectors.get(doc_id)
        if not doc_vector:
            return None
        
        return {
            'doc_id': doc_id,
            'length': self.doc_lengths.get(doc_id, 0),
            'num_unique_terms': len(doc_vector.weights),
            'norm': doc_vector.norm,
            'top_terms': sorted(doc_vector.weights.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
        }


class RankedRetrieval:
    """排名检索引擎（整合布尔检索和VSM）"""
    
    def __init__(self, boolean_search_engine, vector_space_model):
        """
        :param boolean_search_engine: 布尔检索引擎
        :param vector_space_model: 向量空间模型
        """
        self.boolean_engine = boolean_search_engine
        self.vsm = vector_space_model
    
    def search(self, query, mode='ranked', top_k=10):
        """
        统一检索接口
        :param query: 查询字符串或词项列表
        :param mode: 'boolean' | 'ranked' | 'hybrid'
        :param top_k: 返回结果数
        :return: 检索结果
        """
        if mode == 'boolean':
            # 布尔检索（无排序）
            if isinstance(query, str):
                return self.boolean_engine.search(query)
            else:
                # 词项列表转为AND查询
                query_str = ' AND '.join(query)
                return self.boolean_engine.search(query_str)
        
        elif mode == 'ranked':
            # 排名检索
            if isinstance(query, str):
                # 简单分词
                query_terms = query.lower().split()
            else:
                query_terms = query
            
            return self.vsm.search(query_terms, top_k)
        
        elif mode == 'hybrid':
            # 混合模式：先布尔筛选，再排序
            if isinstance(query, str):
                # 使用布尔检索获取候选集
                boolean_results = self.boolean_engine.search(query)
                query_terms = query.lower().split()
            else:
                # 词项列表：所有文档都是候选
                boolean_results = None
                query_terms = query
            
            # 在候选集上进行排名
            return self._hybrid_search(query_terms, boolean_results, top_k)
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def _hybrid_search(self, query_terms, candidate_docs, top_k):
        """混合检索：在候选集上排名"""
        query_vector = self.vsm.build_query_vector(query_terms)
        
        # 确定候选集
        if candidate_docs is None:
            candidates = self.vsm.doc_vectors.keys()
        else:
            candidates = candidate_docs
        
        # 计算得分
        scores = []
        for doc_id in candidates:
            doc_vector = self.vsm.doc_vectors.get(doc_id)
            if doc_vector:
                similarity = query_vector.cosine_similarity(doc_vector)
                if similarity > 0:
                    scores.append((doc_id, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def compare_modes(self, query, top_k=10):
        """对比不同检索模式的结果"""
        results = {}
        
        # 布尔检索
        try:
            boolean_results = self.search(query, mode='boolean')
            results['boolean'] = {
                'count': len(boolean_results),
                'docs': sorted(boolean_results)
            }
        except:
            results['boolean'] = {'count': 0, 'docs': []}
        
        # 排名检索
        ranked_results = self.search(query, mode='ranked', top_k=top_k)
        results['ranked'] = {
            'count': len(ranked_results),
            'results': ranked_results
        }
        
        # 混合检索
        try:
            hybrid_results = self.search(query, mode='hybrid', top_k=top_k)
            results['hybrid'] = {
                'count': len(hybrid_results),
                'results': hybrid_results
            }
        except:
            results['hybrid'] = {'count': 0, 'results': []}
        
        return results


# --- 演示和测试函数 ---

def demo_tfidf_calculation():
    """演示TF-IDF计算"""
    print("\n" + "="*80)
    print("【演示1】TF-IDF计算")
    print("="*80)
    
    calculator = TFIDFCalculator(tf_scheme='log', idf_scheme='standard')
    
    print("\n假设文档集合有100个文档")
    print("词项 'algorithm' 出现在10个文档中")
    print("在文档doc1中，'algorithm'出现5次，文档总共50个词\n")
    
    term_count = 5
    doc_length = 50
    num_docs = 100
    doc_freq = 10
    
    tf = calculator.compute_tf(term_count, doc_length)
    print(f"TF (log scheme): {tf:.4f}")
    
    idf = calculator.compute_idf(num_docs, doc_freq)
    print(f"IDF (standard): {idf:.4f}")
    
    tfidf = calculator.compute_tfidf(tf, idf)
    print(f"TF-IDF: {tfidf:.4f}")


def demo_vector_operations():
    """演示向量操作"""
    print("\n" + "="*80)
    print("【演示2】文档向量操作")
    print("="*80)
    
    # 创建两个文档向量
    doc1 = DocumentVector("doc1")
    doc1.add_term("information", 0.5)
    doc1.add_term("retrieval", 0.8)
    doc1.add_term("system", 0.3)
    doc1.normalize()
    
    doc2 = DocumentVector("doc2")
    doc2.add_term("information", 0.6)
    doc2.add_term("retrieval", 0.7)
    doc2.add_term("data", 0.4)
    doc2.normalize()
    
    print(f"\ndoc1向量: {doc1.weights}")
    print(f"doc1范数: {doc1.norm:.4f}")
    
    print(f"\ndoc2向量: {doc2.weights}")
    print(f"doc2范数: {doc2.norm:.4f}")
    
    # 计算相似度
    similarity = doc1.cosine_similarity(doc2)
    print(f"\n余弦相似度: {similarity:.4f}")


def demo_vsm_search(vsm):
    """演示VSM检索"""
    print("\n" + "="*80)
    print("【演示3】向量空间模型检索")
    print("="*80)
    
    queries = [
        ["information", "retrieval"],
        ["data", "mining"],
        ["machine", "learning"],
        ["search", "engine"]
    ]
    
    for query_terms in queries:
        print(f"\n{'-'*80}")
        print(f"查询: {' '.join(query_terms)}")
        
        results = vsm.search(query_terms, top_k=5)
        
        if results:
            print(f"Top-{len(results)} 结果:")
            for i, (doc_id, score) in enumerate(results, 1):
                print(f"  {i}. {doc_id}: {score:.4f}")
        else:
            print("  无匹配结果")


def demo_compare_modes(ranked_retrieval):
    """演示不同检索模式对比"""
    print("\n" + "="*80)
    print("【演示4】检索模式对比")
    print("="*80)
    
    query = "information retrieval"
    print(f"\n查询: {query}\n")
    
    results = ranked_retrieval.compare_modes(query, top_k=5)
    
    # 布尔检索结果
    print("布尔检索 (无排序):")
    print(f"  匹配文档数: {results['boolean']['count']}")
    if results['boolean']['docs']:
        print(f"  文档: {results['boolean']['docs'][:5]}")
    
    # 排名检索结果
    print(f"\n排名检索 (TF-IDF):")
    print(f"  返回结果数: {results['ranked']['count']}")
    for i, (doc_id, score) in enumerate(results['ranked']['results'], 1):
        print(f"  {i}. {doc_id}: {score:.4f}")
    
    # 混合检索结果
    if results['hybrid']['count'] > 0:
        print(f"\n混合检索:")
        print(f"  返回结果数: {results['hybrid']['count']}")
        for i, (doc_id, score) in enumerate(results['hybrid']['results'], 1):
            print(f"  {i}. {doc_id}: {score:.4f}")