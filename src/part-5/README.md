# 压缩倒排索引与两种检索系统

这是一个完整的**信息检索系统**，实现了高效的文档索引、词典压缩和布尔检索功能。系统采用跳表（SkipList）作为底层数据结构，支持快速的文档查找和复杂的布尔查询。

---

## 核心功能

### 1. 倒排索引构建
- 读取文档并提取token
- 记录每个token在文档中的位置信息
- 使用SkipList存储posting list，支持O(log n)查找

### 2. 词典压缩
- **Front Coding（前端编码）**: 利用相邻词项的公共前缀，只存储差异部分
- **Blocking（分块）**: 每k个词项形成一个块，只为锚点（anchor）词项创建词典条目

### 3. 布尔检索
支持以下操作符和复杂查询：
- **AND**: 交集操作（同时包含多个词项）
- **OR**: 并集操作（包含任一词项）
- **NOT**: 差集操作（不包含某词项）
- **括号()**: 控制操作优先级

### 4. 向量空间模型

---

## 文件结构

```
project/
├── src/
│   └── part-5/
│       ├── skiplist.py                    # 跳表数据结构实现
│       ├── boolean_search.py              # 布尔检索引擎
│       ├── boolean_search_v2.py           # 布尔检索引擎, 支持复杂查询表达式和短语查询
│       ├── compress_index.py             # 集成布尔检索的系统
│       ├── main.py                       # 主文件
│       ├── test_skiplist_stride.py       # 分析跳表指针步长对存储性能/检索效率的影响
│       ├── test_tfidf_vsm.py             # 测试向量空间模型下的文档检索
│       └── tfidf_vector_space.py         # 向量空间模型构建
├── output_data/                   # 输入文档目录
│   ├── doc1.stw
│   ├── doc2.stw
│   └── ...
└── test/                          # 输出结果目录
    └── compress_index_with_boolean.log
```

---

## 使用方法

### 1. 运行完整系统

```bash
cd $PROJECT
python src/part-5/main.py
```

**功能**:
- 读取 `output_data/` 目录下的所有 `.stw` 文件
- 构建压缩词典和倒排索引
- 演示三种复杂布尔查询
- 输出统计信息和压缩效果分析

### 2. 运行分析跳表指针步长影响测试

``` bash
python src/part-5/test_skiplist_stride.py
```
对应布尔检索第四项要求

### 3. 运行向量空间模型测试

```bash
python src/part-5/test_tfidf_vsm.py
```

**功能**:
- TF-IDF计算验证 - 验证权重计算正确性
- 文档向量分析 - 查看向量表示和Top权重词项
- 排名检索测试 - 不同查询的检索结果
- 查询扩展效果 - 查询长度对结果的影响
- 文档相似度 - 同主题vs不同主题文档
- 模式对比 - 布尔检索vs排名检索
- TF方案对比 - 不同计算方案的效果
- 性能分析 - 查询响应时间测试
- 结果质量分析 - 精确率和召回率

---

## 布尔查询示例

### 示例1: AND操作
```
查询: apple AND banana
含义: 查找同时包含 "apple" 和 "banana" 的文档
结果: {doc1, doc4, doc6}
```

### 示例2: 复合操作
```
查询: (apple OR banana) AND NOT cherry
含义: 包含apple或banana，但不包含cherry的文档
结果: {doc1, doc4}
```

### 示例3: 嵌套表达式
```
查询: (apple AND banana) OR (cherry AND NOT date)
含义: 
  - 子表达式1: apple AND banana → {doc1, doc4, doc6}
  - 子表达式2: cherry AND NOT date → {doc2, doc6}
  - 最终结果: 两个子集的并集
结果: {doc1, doc2, doc4, doc6}
```

---

## 技术实现细节

### 跳表（SkipList）

**优势**:
- 平均O(log n)的查找时间
- 简单的插入和删除操作
- 天然支持有序遍历

**实现**:
```python
class SkipList:
    def insert(self, value)      # 插入文档ID和位置
    def search_docid(self, id)   # 查找文档ID
    def delete(self, value)      # 删除posting
```

### 词典压缩算法

**Front Coding示例**:
```
原始词项: apple, apply, apricot
压缩后:
  - anchor: 0|5|apple
  - term2:  |5|0|y        (前缀长度5，后缀"y")
  - term3:  |3|4|ricot    (前缀长度3，后缀"ricot")
```

**Blocking示例**:
```
Block 0 (k=4): [apple, apply, apricot, banana]
  → 只为 "apple" 创建词典条目
  
Block 1: [cherry, date, elderberry, fig]
  → 只为 "cherry" 创建词典条目
```

### 布尔检索算法

**核心操作**:
```python
# 交集 (AND)
result = posting_list1 & posting_list2

# 并集 (OR)
result = posting_list1 | posting_list2

# 差集 (NOT)
result = all_documents - posting_list
```

**表达式解析**:
- 采用递归下降解析
- 支持任意嵌套的括号
- 正确处理操作符优先级

---

## 性能分析

### 空间复杂度

| 组件 | 原始存储 | 压缩后 | 压缩率 |
|------|---------|--------|--------|
| 词典字符串 | O(n×L) | O(n×L/k) | ~50% |
| 词典索引 | O(n) | O(n/k) | 75% |
| Posting Lists | O(n×d) | O(n×d) | - |

其中：
- n: 词项总数
- L: 平均词项长度
- k: 块大小
- d: 平均每词项的文档数

### 查询时间复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 单词查询 | O(log n) | SkipList查找 |
| AND操作 | O(d₁ + d₂) | 遍历两个posting list |
| OR操作 | O(d₁ + d₂) | 遍历两个posting list |
| NOT操作 | O(D) | D为文档总数 |

---

## 注意事项

1. **文档格式**: 输入文件每行一个token，自动记录行号作为位置
2. **文件扩展名**: 默认读取 `.stw` 文件
3. **查询语法**: 操作符必须大写（AND/OR/NOT），词项区分大小写
4. **括号匹配**: 确保查询表达式中括号正确匹配
