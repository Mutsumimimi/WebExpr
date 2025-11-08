（1） 在倒排表中加入词项的位置信息，以应对短语检索需求
（2） 任选两种课程中介绍过的索引压缩方法加以实现，如按块存储、前端
编码等，并比较压缩后的索引在存储空间上与原索引的区别。

step1:
``` python
python src/part-4/step-1/add_pos.py
```
得到带有skip list和词项位置信息的倒排表

step2:
``` python
python src/part-4/compress_index.py
```
将所有词项压缩成一个词典字符串 term_string, 并以N=4的间隔设置词典索引。

TODO:
- 修改Front Coding的逻辑
- 可能需要移除store_dict.py