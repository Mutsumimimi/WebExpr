让我们理一下思路，先不讨论具体代码实现。我们不把词典与倒排表放在一起存储，而是分别存储为不同的文件，通过页指针关联。这样token与其对应的Posting list就能“分开”。
先考虑词典的存储方式，采用最简单的顺序存储。
由于我们将词典视作单一字符串，词典的存储结构大致是:
- 词典字符串(TYPE = str)
- Dictionary's element(实际上就是token及其related info)
    - token 指针(TYPE = str *), 指向 token 在字符串中的位置
    - token 长度(TYPE = int)
    - frequency 出现频率(TYPE = int)
    - PostList-ref 倒排索引的指针 **重要**

**Task:** 我们需要采用前端编码的方式对词典索引进行压缩。

再考虑倒排表存储。目前倒排表采用SkipList类加以实现，其结构如下：
```
SkipList
    ├── max_level: 设定的跳表的最大层数
    ├── p: 第i层的任一元素在第i+1层出现的概率
    ├── header: 头节点(Node类型)
    │   ├── .value: 元素的值，在 posting list 中是包含文档序号 doc_id 和出现位置 pos 的类Value
    │   └── .forward: 跳表指针, 元素个数为 level+1 的数组, forward[i] 表示第i层的节点的后继
    └── level: 节点的层数，表示某个元素有几个(层)跳表节点
```
我们需要让词典元素中的PostList-ref指针指向 SkipList，即
`Dictionary's element.PostList-ref := SkipList`
这样就为实现倒排表的静态存储（存放到文件）提供基础（因为我们不能一直让词典和倒排表同时放在内存中）。
**Task:** 我们需要实现倒排表的静态存储和读取。

方案一：
1. 实现倒排表的静态存储。读取 token 对应的倒排表，将 {doc_id 1:[pos 1, pos 2, ...], doc_id 2:[...], ..}写入 <token_file>.
2. 实现 <token_file> 的读取。当查询请求到 token 时，读取对应的 <token_file> 到内存，仍然以倒排表的数据结构存放在内存。
3. （可选）设计跳表指针的静态存储。在每个token对应的倒排表没那么大，词典本身成为最大的存储开销时，不必再设计跳表指针。

方案二：
1. 不采用静态存储倒排表的方案，而是只静态存储词典字符串。词典字符串依照简单的顺序存储方式。此时 token 指针指向词典文件中的偏移量，token 的倒排索引（包括跳表索引）仍然动态保存在内存里。
2. 对词典文件进行压缩。有两种方式：按块存储(Blocking)和前端编码(Front Coding)。
    - 按块存储：每k个词项存储一个指针，如k=4. 在词典文件中需要额外1个字节用于表示词项长度. 
    - 前端编码：使用特殊字符表示前缀使用