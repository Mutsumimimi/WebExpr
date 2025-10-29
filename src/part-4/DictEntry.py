class DictionaryEntry:
    """
    存储倒排索引词典中的单个词项的元数据。
    """
    def __init__(self, token, PostList_ref):
        # 1. 词项 (Token)
        self.token = token
        
        # 2. 倒排记录表指针 (这里用 Posting List 实例作为抽象指针)
        # 在实际系统中，这会是一个指向文件或块的字节偏移量/ID。
        self.PostList_ref = PostList_ref
        
        # 3. 出现频率 (Document Frequency, df)
        # 统计包含该词项的文档总数（即 Posting List 的长度）。
        self.document_frequency = self._calculate_df() 
        
        # 4. 词项指针 (用于内部加速查找，这里简化为 None)
        # 在实际系统中，可能是指向 B树或哈希表中的下一个节点/桶。
        self.internal_pointer = None 
    
    def _calculate_df(self):
        """
        计算文档频率：遍历 SkipList 的底层链表，统计节点数量。
        """
        if not self.PostList_ref:
            return 0
        
        count = 0
        # 从 SkipList 的底层 (Level 0) 开始遍历
        current = self.PostList_ref.header.forward[0]
        while current:
            count += 1
            current = current.forward[0] # 沿着常规指针前进
        return count
    
    def __repr__(self):
        return (f"Entry(df={self.document_frequency}, "
                f"PL_Ref={self.PostList_ref.level} Levels)")

# 注意：为了让这个方案工作，SkipList 类必须在前面定义，
# 并且 SkipList.header.forward[0] 必须是底层链表的起点。