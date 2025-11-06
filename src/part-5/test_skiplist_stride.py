'''
part5布尔查询第四题
'''
import time
import random
import skiplist
import os, sys

def run_performance_test(n_elements, p_value, max_level=16):
    """
    运行跳表插入和搜索性能测试
    :param n_elements: 要插入的元素数量
    :param p_value: 跳表的概率 p
    :param max_level: 最大层数
    :return: 插入时间, 搜索时间
    """
    sl = skiplist.SkipList(max_level, p_value)
    
    # 1. 生成数据
    # 为了避免偏序影响，我们使用随机且唯一的doc_id
    ids_to_insert = list(range(n_elements))
    random.shuffle(ids_to_insert)
    
    # 2. 插入测试
    start_time = time.perf_counter()
    for doc_id in ids_to_insert:
        # 假设 pos 总是 1，因为对性能影响不大
        sl.insert(skiplist.Value(doc_id, 1))
    insert_time = time.perf_counter() - start_time

    # 3. 搜索测试
    # 测试搜索所有插入的元素，以获得平均搜索时间
    search_ids = list(range(n_elements))
    random.shuffle(search_ids)
    
    start_time = time.perf_counter()
    for doc_id in search_ids:
        # 注意: 您的 search_docid 方法返回 True/False
        found = sl.search_docid(doc_id)
        if not found:
             # 如果出现这种情况，可能是实现有问题，这里可以跳过或记录错误
             pass 
             
    search_time = time.perf_counter() - start_time
    
    return insert_time, search_time

def main_test_harness(n_elements=100000,max_level=16):
    """主测试套件"""
    
    os.makedirs("./test", exist_ok=True)
    filename = "./test/test_skiplist_stride.log"
    with open(filename, 'w', encoding='utf-8') as file:
        STDOUT = sys.stdout
        sys.stdout = file
        
        print(f"开始跳表性能测试 (总元素数量 N={n_elements})")
        print("-" * 50)
        print(f"{'p 值':<10} | {'插入时间 (秒)':<15} | {'搜索时间 (秒)':<15}")
        print("-" * 50)

        p_values = [0.25, 0.5, 0.75] # 要测试的概率 p 值
        max_level = 16  # 设定一个最大层数
        for p in p_values:
            insert_t, search_t = run_performance_test(n_elements, p, max_level)
            print(f"{p:<10} | {insert_t:<15.6f} | {search_t:<15.6f}")
            
        sys.stdout = STDOUT
        print(f"跳表性能测试结果已经写入到'{filename}'中！")

if __name__ == '__main__':
    # 建议先从较小的 N 开始 (例如 100000)，如果机器性能允许，再增大 (例如 1000000)
    main_test_harness(n_elements=100000) 
    # 您也可以测试更大的数据量：
    # print("\n--- 增大到 500,000 个元素 ---")
    # main_test_harness(n_elements=500000)