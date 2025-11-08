# 信息检索实验
实验完成了一个完整的信息检索系统，实现了文档解析和规范化处理，构建倒排表及拓展优化、多种方式的信息检索。这个系统完成了实验要求中的必做内容，即：
- 对指定文档进行文字处理，提取规范化词项
- 构建与优化倒排表和索引
- 基于倒排表进行文档查询

下面按照实验要求中的顺序一一介绍实验成果。

---

## 文件结构
```
.
├── Dataset                         # 数据集，原始的数据来源
├── output_data                     # 存放part-2的输出文件,是Dataset的输出
├── src                             # 存放源代码
│   ├── part-2
│   │   ├── filter_words.py
│   │   ├── generate_filelist.py
│   │   ├── main-1.py
│   │   ├── mytokenize.py
│   │   ├── normalize.py
│   │   └── remove_stopwd.py
│   ├── part-3
│   │   ├── invert_index.py
│   │   └── skiplist.py
│   ├── part-4
│   │   ├── step-1
│   │   │   └── add_pos.py
│   │   ├── compress_index.py
│   │   ├── README.md
│   │   ├── skiplist.py
│   │   └── solution.md
│   └── part-5
│       ├── boolean_search.py
│       ├── boolean_search_v2.py
│       ├── compress_index.py
│       ├── main.py
│       ├── README.md
│       ├── skiplist.py
│       ├── test_skiplist_stride.py
│       ├── test_tfidf_vsm.py
│       └── tfidf_vector_space.py
├── stanford-corenlp-4.5.10         # 自然语言分析工具，用于tokenize
├── test                            # 日志文件，存放part3~part5的分析日志
│   ├── all_token.log
│   ├── compress_index.log
│   ├── compress_index_with_boolean.log
│   ├── inverted_index.log
│   ├── part-4.log
│   ├── test_skiplist_stride.log
│   └── test_tfidf_vsm.log
├── filelist.txt                    # 运行 stanford-corenlp 工具时的依赖
├── part-2.sh                       # 执行part-2
├── README.md
├── requirements.txt                # Python环境
└── tokenize.sh                     # 用于生成filelist
```

### 配置环境
#### 1. 配置Python
首先在Linux中新建工作区，打开命令行
``` bash
python3 --version
# Python 3.12.3
```
本次实验使用python3.12
``` python
python3 -m venv .venv  # 创建虚拟环境
source .venv/bin/activate  # 激活
pip install -r requirements.txt
```
#### 2. 配置nltk
主要是nltk包的下载
在命令行里打开python
``` python
import nltk
nltk.download()
```
依照提示进行下载。或者直接nltk.download('all')

#### 3.下载Stanford-CoreNLP-4.5.10
直接去官网上下载
`https://stanfordnlp.github.io/CoreNLP/download.html`
当前提供的文件夹中已配置好该工具包。

#### 4.划定数据集
本次实验中从所提供的meetup数据中的 Event 类文件随机挑选出100个文件。实际可以尝试其他类别的文件，数量合适即可。
在项目根目录中新建`Dataset`文件夹，并将所选文件复制到该目录下。

## 实验介绍

### 一. 文档解析与规范化处理

实验划分的数据集Dataset是从 Event 类文件中随机挑选的 100 个文件，位于根目录下的`Dataset`。本模块对Dataset中的所有文档进行解析和规范化处理，输出目录位于根目录下的`output_data`.
**操作办法：**
``` bash
$ ./part-2.sh
```
这将一次执行src/part-2中所有相关代码，得到相应的经规范化处理的待检索文档。

#### (1) 

```
结合自选编程语言中的工具包，解析文档中所需的部分内容。文件范
围和内容自定（但至少应包括 Event 类文件及其中的 Description 部分
内容），并将从一个文件中解析出的内容合并为一篇待检索的文档。
```

采用`python`工具包，使用`xml` `html` `re`库查找数据集文档中的<description>标签，并提取内容合并为一篇待检索的文档。
输入格式是.xml文件，输出格式是后缀名为.desc的文件。
具体实现在`src/part-2/main-1.py`。

#### (2)

```
对文档中的文本进行分词处理，即将成段的文字拆分为单字词和短语。
短语可简单根据连字符等制定规则进行拆分，也可引入外部词库协助
拆分。当然，如果想偷懒的话，也可以直接只保留单字词（例如，将
To be or not to be 拆成 6 个基本单词）。
```

使用了Stanford Corenlp项目。这是一个自然语言处理工具包，集成了很多非常实用的功能，包括分词，词性标注，句法分析等等，这里使用了这个项目的分词工具，将成段的文字拆分成单字词，即tokenize.
在项目根目录运行以下命令
``` bash
SRC_PATH="src/part-2"
$ python ${SRC_PATH}/generate_filelist.py
$ ./tokenize.sh
```
从上一部分得到的待检索文档，提取出token。输出每行一个token的文件。
输入格式为: \*.desc
输出格式为: \*.desc.conll

#### (3)
```
根据第 3 节课内容，对分词后的所有单词进行规范化处理，从而形成
规范化的词项（Token），包括并不限于去除停用词、数字、标点符号
和其他特殊字符，对单词进行归一化处理（词干提取、词形还原）等
等。该部分可通过手动编写规则进行，也可以通过寻找工具包来进行。
```
上一阶段得到的 \*.desc.conll 文件中，除了后续查询时有用的单词外，还有很多干扰token，如标点符号，数字等等。因此先进行清理操作：
``` bash
python ${SRC_PATH}/filter_words.py
# 读取 input 文件，删除所有非“单词”的行，并将结果写入 *.flt
```
这一部分主要使用了正则表达式对“非单词”的词项进行识别。经过清理操作后，进一步进行归一化处理。归一化处理采用了`nltk`工具包，使用库中`nltk.stem.WordNetLemmatizer`方法进行词形还原(lemmatize).
``` bash
python ${SRC_PATH}/normalize.py
```
然后是去除停用词。使用`nltk.corpus.stopwords`模块识别停用词。
``` bash
python ${SRC_PATH}/remove_stopwd.py
```
至此，通过以上操作我们得到了干净、可供检索的所有词项。当前经处理得到的文件为`output_data/*.stw`，在后续部分中都会对这些文件处理。
### 二. 倒排表的构建

```
根据第 4 节课内容，对前一部分所获得的所有文档中的所有规范化词项构建倒排表。

为实现面向倒排表的快速检索，设计合适的跳表指针。
```
该部分将文档集合处理成倒排索引，并集成了 skiplist.py 中定义的跳表，实现了倒排表的构建。

**构建倒排索引**

在`invert_index.py`中，将上一部分中得到的数据看成以下格式：

    type=dictionary
        { 
            doc_1：['i', 'am', 'a', 'student']
            doc_2: ['i', 'have', 'a', 'computer']
            ...
        }

为了得到倒排表，需要从所有文档中检索单一的token, 并记录token出现的文档编号，即

    type=dictionary
        { 
            'i':  [doc1, doc2]
            'am': [doc1]
            'a':  [doc1, doc2]
            ...
        }

以这样的思路,`invert_index()`构建了倒排索引。

**跳表数据结构**:

skiplist.py

该文件实现了跳表（SkipList）数据结构。
主要功能：
- Node 类: 定义了跳表中的基本节点，包含值 (value) 和一个指向不同层级后续节点的数组 (forward)。

- SkipList 类:

    随机层级生成 (random_level): 根据概率 $P$ 和最大层级限制，为新插入的节点随机分配层级，这是跳表高效查询的基础。

    搜索 (search): 实现了跳表的高效查询功能，时间复杂度平均为 $O(\log n)$。

    插入 (insert): 将新值插入到跳表中，并根据随机层级更新相应的指针。

    删除 (delete): 从跳表中移除指定的值。

当下实现的跳表结构有一个参数`P`表示一层中任一节点出现在下一层的概率。通常把`P`设置为`0.5`，可以通过实验发现这是效率最高的值（这个实验在第五部分中的布尔检索模块）。因此该跳表是多层且层高随机的。同时为了防止层高过高，设置了另一个参数`MAX_LEVEL`, 实验中设置为`16`, 通常情况下这个值的设定不会对实验造成太大影响。

**跳表集成 (add_skiplist):**

接收上一步生成的倒排列表，对每个 Token 的文档 ID 列表进行排序，然后将这些有序的文档 ID 依次插入到一个新的 SkipList 实例中。
最终的倒排索引结构是：`{ Token: SkipList(doc_id_s) }`。

**操作方法**
``` bash 
$ python src/part-3/invert_index.py
```
将会得到两个输出文件
`test/all_token.log`和`test/inverted_index.log`，
分别涵盖了从数据集的所有文档中得到的词项和倒排索引记录。

### 三. 倒排表的扩展与优化

    （1） 在倒排表中加入词项的位置信息，以应对短语检索需求。
    （2） 任选两种课程中介绍过的索引压缩方法加以实现，如按块存储、前端
    编码等，并比较压缩后的索引在存储空间上与原索引的区别

#### （1）位置信息查询

这个版本的 skiplist.py 对跳表进行了升级，使其能够存储更复杂的倒排列表（Posting List）条目。

Value 类: 引入 Value 类来封装 Posting List 中的条目。每个 Value 对象存储两个关键信息：

- id (doc_id): 文档的唯一标识符。

- pos (positions): 词项在文档中出现的所有位置的列表。

SkipList 逻辑更新:

- Node 存储的不再是简单数值，而是 Value 对象。

- 跳表的搜索、插入、删除逻辑（如在 search 和 insert 中）全部基于 Value.id 进行比较和排序，确保 Posting List 仍然按文档 ID 有序，同时携带了位置信息。

**操作方法**
``` bash
python src/part-4/ste-1/add_pos.py
```
得到一个输出文件`test/part-4.log`，里面输出了token对应的倒排索引，包括token在文档中出现的位置。如

    aboard:	(11407898: [125]) -> (20146641: [7, 22])

#### （2）索引压缩
compress_index.py - 词典压缩（Blocking + Front Coding）

该文件对倒排索引的词典（Vocabulary）部分进行存储优化，采用了按块存储 (Blocking) 和前端编码 (Front Coding) 两种压缩技术。

主要功能：

- 词典条目结构 (DictionaryEntry): 定义了存储压缩信息的元数据结构，包括块 ID (block_id)、在压缩字符串中的偏移量 (term_string_offset) 和压缩长度 (compressed_length)。

- 前端编码 (front_coding_block): 这是核心压缩逻辑。它将词项分组（块大小为 BLOCK_SIZE），并计算块内词项之间的公共前缀，只存储差异部分（后缀），从而减少存储空间。

- 词项重建 (reconstruct_token_from_string): 演示了如何根据词典条目的元数据和压缩后的字符串，从 Anchor Token (块的首个词项) 开始，重建块内任意位置的完整 Token。

- 空间对比: run 函数演示了构建压缩词典的过程，并输出了原始 Token 字符串总长度和压缩后字符串总长度的对比。

**操作方法**
``` bash
python src/part-4/compress_index.py
```
得到输出文件`./test/compress_index.log`,可以看到压缩后的词典字符串 (TERM_STRING)和对应的词典索引。

### 四. 多种形式的信息检索

#### A.布尔检索
```
实验要求：
（1） 自行设计不少于 3 种复杂查询条件，以布尔表达式的形式呈现。并通过实验分析同一个布尔表达式的不同处理顺序对时间开支的影响。
（2） 根据倒排表进行检索，并比较索引压缩前后在检索效率上的差异。
（3） 至少设计 1 次面向短语的检索，并分析加入词项位置信息的扩展倒排表在应对短语检索任务时的效果。
（4） 选择不同的跳表指针步长，并分析其对存储性能/检索效率的影响。
```

在上一阶段的基础上，加入布尔检索引擎`boolean_search.py`.
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

文件结构如下：

| 文件名 | 核心功能 | 作用描述 |
|-----|--------|-----------|
|main.py|系统驱动与集成|负责读取数据、调用索引构建模块、初始化检索引擎，并执行性能分析。|
|skiplist.py|核心数据结构|提供支持 $O(\log n)$ 检索的带位置信息的倒排列表容器。|
|compress_index.py|索引构建与压缩|负责生成倒排列表（Posting Lists）并对词典（Vocabulary）进行前端编码压缩。|
|boolean_search_v2.py|查询处理引擎|实现对复杂布尔查询表达式和短语查询的解析与执行。|
|test_boolean_search.py|测试用例|定义用于功能验证和演示的测试数据集和查询用例。|

**复杂查询处理** (`boolean_search_v2.py`)

该文件是系统的核心检索逻辑，它初始化时接收压缩词典和倒排列表，并提供查询能力：

1.复杂布尔查询:

- 支持 AND（交集）、OR（并集）和 NOT（差集）操作。

- 通过对查询字符串的分词 (tokenize_query) 和中缀转后缀等内部逻辑（尽管代码中可能简化为直接求值），实现对含括号的复杂表达式的正确求值。

2.短语查询 (phrase_query):

- 这是基于位置索引的核心功能。它首先找到包含所有短语词项的文档（布尔 AND 操作），然后对这些文档的 Posting List 进行邻近性检查。

- 通过比较相邻词项在文档中的位置（p2 = p1 + 1），确保短语中的词项是连续且有序出现的，从而返回精确匹配的文档集合。

3.性能分析: 包含 `analyze_query_performance` 函数，能够统计查询时间、Posting List 大小，用于评估检索效率。

**系统集成**
`main.py` (系统驱动):

端到端流程: 驱动整个 IR 系统的运行，流程为：读取文档 -> 收集 Token -> 构建压缩词典和倒排列表 -> 初始化布尔检索引擎。

结果演示: 打印词典压缩率和布尔查询的性能分析结果，用于直观展示系统的有效性和效率。

#### 使用方法

```bash
python src/part-5/main.py
```

**功能**:
- 读取 `output_data/` 目录下的所有 `.stw` 文件
- 构建压缩词典和倒排索引
- 演示三种复杂布尔查询
- 输出统计信息和压缩效果分析

输出的分析文件在`test/compress_index_with_boolean.log`



#### 回答实验要求中的问题
##### (1) 通过实验分析同一个布尔表达式的不同处理顺序对时间开支的影响
在`main.py`的输出分析文件中，有以下内容：
```
查询1: (book AND club) OR (chat AND date)
涉及词项: ['book', 'club', 'chat', 'date']
Posting List大小: {'book': 8, 'club': 6, 'chat': 1, 'date': 8}
搜索时间：0.000011       
最终结果集大小: 2

查询2: (book OR (chat AND date)) AND (club OR (chat AND date))
涉及词项: ['book', 'chat', 'date', 'club']
Posting List大小: {'book': 8, 'chat': 1, 'date': 8, 'club': 6}
搜索时间：0.000012       
最终结果集大小: 2

查询3: ((book OR chat) AND (book OR date)) AND ((club OR chat) AND (club OR date))
涉及词项: ['book', 'chat', 'date', 'club']
Posting List大小: {'book': 8, 'chat': 1, 'date': 8, 'club': 6}
搜索时间：0.000015       
最终结果集大小: 2
```
可以看到，我们设置了三个具有相同逻辑的布尔表达式，其最简表达式是查询1`(book AND club) OR (chat AND date)`, 最复杂的形式是查询3.三种查询表达式将会返回同样的倒排索引结果。
结果显示采用最简表达式的查询1搜索时间最短，查询效率最高。
##### (2) 比较索引压缩前后在检索效率上的差异
压缩前：
理论上会采用定长存储的方式，即给每个token分配固定字节的空间（如20字节）
```
{
    token,              # 词项
    df(document frequency), # 文档频率
    postinglist_ref     # 倒排指针
}
```
按照二分查找方式计算的时间复杂度为`O(log(n))`
压缩后：
由于采用了将词典视作单一字符串、按块存储和前段编码的方式，数据存储逻辑发生改变。
```
{
    term_string,        # 词典字符串，以字典序存储了所有token，并在每个token前用一个数字表示token长度
    BlockEntry
    {
        token_ref,      # 指向词典字符串中词项的指针 -> term_string[offset]
        list::Tokens[BLOCK_SIZE]
        {
            df,             # 文档频率
            postinglist_ref # 倒排指针
        }
    }
}
```
按块存储下，每个块(block)只有块的头部(anchor token)会设置`DictEntry.token_ref`
检索时，先以块为单位进行二分查找，只根据BlockEntry.token_ref指向的anchor_token来比较大小；当锁定块的位置后，在块内顺序遍历词项。
块外查询的时间复杂度为`O(log(n))`, 块内为`O(N)`

##### (3) 分析加入词项位置信息的扩展倒排表在应对短语检索任务时的效果

在拓展词项位置信息的倒排表中，布尔检索得以查询token的`Node.Value.pos`和`Node.Value.doc_id`属性，并判断查询词是否出现在同一文档中并且相邻。在`boolean_search_v2.py`中，下面这一函数就做了这件事。
``` python
def _verify_phrase_positions(self, doc_id, phrase_tokens, all_positions):
        """
        验证短语中的词项是否在文档中按顺序相邻出现
        :param doc_id: 文档ID
        :param phrase_tokens: 短语词项列表
        :param all_positions: 每个词项的位置信息列表
        :return: True if 短语匹配，False otherwise
        """
```

##### (4)分析不同的跳表指针步长对存储性能/检索效率的影响
在命令行中：
``` bash
python src/part-5/test_skiplist_stride.py
```

可以看到，在之前的跳表结构实现的基础上，对参数`P`的值为`0.25,0.5,0.75`的情况分别做出分析。结果如下：
```
--------------------------------------------------
p 值        | 插入时间 (秒)        | 搜索时间 (秒)       
--------------------------------------------------
0.25       | 0.689686        | 0.521619       
0.5        | 0.748508        | 0.442618       
0.75       | 2.585020        | 4.818281       
```
由于`P`值代表了每层节点出现在下一层的几率，`P`值越小，每一层的步长就越大。在数据集规模很小的情况下（100个文档，约3000个词项），理论上跳表步长应该设置的较小一点，至少应该低于`0.5`.

#### B.向量空间模型

以下是part-5源码的文件结构
```
└── part-5/
    ├── skiplist.py                    # 跳表数据结构实现
    ├── boolean_search.py              # 布尔检索引擎
    ├── boolean_search_v2.py           # 布尔检索引擎, 支持复杂查询表达式和短语查询
    ├── compress_index.py             # 集成布尔检索的系统
    ├── main.py                       # 主文件
    ├── test_skiplist_stride.py       # 分析跳表指针步长对存储性能/检索效率的影响
    ├── test_tfidf_vsm.py             # 测试向量空间模型下的文档检索
    └── tfidf_vector_space.py         # 向量空间模型构建
```
**运行方法**
``` bash
python src/part-5/test_tfidf_vsm.py > test/test_tfidf_vsm.log
```
**主要功能**:
- TF-IDF计算验证 - 验证权重计算正确性
- 文档向量分析 - 查看向量表示和Top权重词项
- 排名检索测试 - 不同查询的检索结果
- 查询扩展效果 - 查询长度对结果的影响
- 文档相似度 - 同主题vs不同主题文档
- 模式对比 - 布尔检索vs排名检索
- TF方案对比 - 不同计算方案的效果
- 性能分析 - 查询响应时间测试
- 结果质量分析 - 精确率和召回率

部分输出如下：
```
【测试1】TF-IDF计算验证
====================================================================================================

词项                   文档频率            IDF值            说明                            
----------------------------------------------------------------------------------------------------
apple                3               1.5185          常见词（中等IDF）                    
data                 1               1.9956          罕见词（高IDF）                     
air                  1               1.9956          罕见词（高IDF）                     
learn                11              0.9542          高频词（低IDF）

【测试3】排名检索测试
====================================================================================================

查询: information retrieval (信息检索主题)

Top-5 结果:
  1. 20083991        得分: 0.0049
  2. 11409522        得分: 0.0047
  3. 20186881        得分: 0.0028
  4. 20185691        得分: 0.0025
  5. 20194751        得分: 0.0025

----------------------------------------------------------------------------------------------------
查询: data mining (数据挖掘主题)

Top-1 结果:
  1. 11407548        得分: 0.0018

----------------------------------------------------------------------------------------------------
查询: machine learning (机器学习主题)
  无匹配结果

----------------------------------------------------------------------------------------------------
查询: algorithm data (算法与数据)

Top-1 结果:
  1. 11407548        得分: 0.0018

----------------------------------------------------------------------------------------------------
查询: search system (搜索系统)

Top-3 结果:
  1. 20162911        得分: 0.0109
  2. 11405924        得分: 0.0054
  3. 10550943        得分: 0.0018
```
