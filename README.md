part2: 文档解析与规范化处理
part3: 构建倒排表，设置跳表指针
part4: 加入词项的位置信息; 实现两种索引压缩方法
.
├── Dataset                 # 数据集，原始的数据来源
├── filelist.txt            # stanford-corenlp 的依赖
├── filter_words.py         # part2
├── generate_filelist.py    # 生成filelist.txt(运行前确保只有.desc文件)
├── invert_index.py         # part3 倒排表
├── main-1.py               # part2
├── normalize.py            # part2
├── output_data             # 存放中间的数据输出文件
├── part-2.sh               # 执行part2
├── README.md
├── remove_stopwd.py        # part2
├── requirements.txt        # Python环境依赖
├── src
│   ├── part-3
│   │   ├── invert_index.py
│   │   └── skiplist.py
│   └── part-4
│       ├── add_pos.py
│       └── skiplist.py
├── stanford-corenlp-4.5.10 # 自然语言分析工具，用于tokenize
├── test                    # 存放part3,part4输出
│   ├── inverted_index.log
│   └── part-4.log
├── test copy
├── test.copy.conll
└── tokenize.sh             # part2

ps: 1.运行前检查脚本是否有执行权限，如果没有使用`chmod +x <file>`命令
2.检查python配置，创建虚拟环境，并检查python脚本是否使用指定的Python

part2不再采用词干提取，改为词形还原，效果比之前好

### 配置环境
#### 1. 配置Python
``` python
python3 -m venv .venv  # 创建虚拟环境
source .venv/bin/activate  # 激活
pip install -r requirements.txt
```
主要是nltk包的下载
在命令行里
``` python
import nltk
nltk.download()
```
依照提示进行下载。或者直接nltk.download('all')

#### 2.下载Stanford-CoreNLP-4.5.10
直接去官网上下载
`https://stanfordnlp.github.io/CoreNLP/download.html`