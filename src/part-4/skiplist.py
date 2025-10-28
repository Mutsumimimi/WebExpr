import random

'''
与part-3中的同名文件不同，添加了Value的类，以及SkipList逻辑的改动0]'[v]
'''

class Value:
    def __init__(self, doc_id, pos):
        self.id = doc_id
        self.pos = pos

class Node:
    def __init__(self, value, level):
        self.value = value
        self.forward = [None] * (level + 1) # [None]是Python中的关键字，用于初始化元素
        
class SkipList:
    '''
    max_level: 跳表的最大层数
    p: 第i层的任一元素在第i+1层出现的概率
    header: 头节点(Node类型)
    ├── header.value: 元素的值，在 inverted_list 中是文档序号 doc_id
    └── header.forward: 元素个数为 level+1 的数组, forward[i] 表示第i层的节点的后继
    level: 节点的层数，表示某个元素有几个(层)跳表节点
    '''
    def __init__(self, max_level, p):
        self.max_level = max_level
        self.p = p
        self.header = Node(-1, max_level)
        self.level = 0
        
    def random_level(self):
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level
    
    def search_docid(self, id):
        current = self.header
        
        # 找到该层最后一个键值小于 key 的节点，然后走向下一层
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].value.id < id:
                current = current.forward[i]
                
        # 现在是小于，所以还需要再往后走一步
        current = current.forward[0]
        return current and current.value.id == id
    
    def insert(self, value):
        update = [None] * (self.max_level + 1)
        current = self.header
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].value.id < value.id:
                current = current.forward[i]
            update[i] = current
        level = self.random_level()
        if level > self.level:
            for i in range(self.level + 1, level + 1):
                update[i] = self.header
            self.level = level
        new_node = Node(value, level)
        for i in range(level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
            
    def delete(self, value):
        update = [None] * (self.max_level + 1)
        current = self.header
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].value.id < value:
                current = current.forward[i]
            update[i] = current
        current = current.forward[0]
        if current and current.value.id == value:
            for i in range(self.level + 1):
                if update[i].forward[i] != current:
                    break
                update[i].forward[i] = current.forward[i]
            while self.level > 0 and not self.header.forward[self.level]:
                self.level -= 1