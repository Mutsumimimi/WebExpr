#!/usr/bin/python3
import os
import xml.etree.ElementTree as ET
import re
import html

# 存储所有提取到的 description 内容
all_descriptions = []
xml_directory = 'Dataset' # 假设XML文件都在这个目录下
output_path = 'output_data/'

def clean_html(text):
    pattern_1 = r'<a[^>]*>(.*?)</a>'    # hyperlink
    pattern_3 = r'<(img|span|p)[^>]*?/?>' # index
    pattern_2 = r'</?[\w]+\s*/?>'   # <b>,</b>,<br>...包括</a>
    pattern_4 = r':-\)' # 混乱符号

    cleaned_text = re.sub(pattern_1, '', text, flags=re.IGNORECASE)
    cleaned_text = re.sub(pattern_3, '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(pattern_2, '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(pattern_4, ' ', cleaned_text, flags=re.IGNORECASE)
    
    return cleaned_text

def parse_xml_file(file_path):
    descriptions = []
    
    # 解析整个 XML 文件
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 使用 XPath 或直接 tag 名称查找所有 <description> 标签
    # 假设 <description> 在 XML 结构中可能出现在任何地方
    # 使用 findall(".//tag") 会在整个子树中搜索
    for desc_element in root.findall('.//description'):
        # .text 属性获取标签的文本内容
        content = html.unescape(desc_element.text)
        # content = desc_element.text
        if content:
            # 清理首尾空白字符
            cleaned_content = content.strip() 
            # 删除无用的html标签
            cleaned_content = clean_html(cleaned_content)
            descriptions.append(cleaned_content)
            
    return descriptions

def create_summary_document(descriptions_list, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as f:
        # f.write("# XML 文件内容汇总\n\n")
        # f.write("---" * 10 + "\n\n")
        
        # 遍历所有描述并写入文件
        for i, description in enumerate(descriptions_list, 1):
            # f.write(f"## 描述 {i}\n") # 可以为每条描述加一个标题
            f.write(description)
            f.write("\n")
            # f.write("\n\n" + "-"*30 + "\n\n") # 分隔符

    print(f"汇总文档已成功创建: {output_filename}\n")
    

def run():
    # 遍历目录
    for filename in os.listdir(xml_directory):
        if filename.endswith('.xml'):
            file_path = os.path.join(xml_directory, filename)
            print(f"--- 正在处理文件: {filename} ---")
            
            # 接下来调用解析函数
            try:
                descriptions_from_file = parse_xml_file(file_path)
                # all_descriptions.extend(descriptions_from_file) # 将提取的内容加入总列表
                basename, externname = os.path.splitext(filename)
                create_summary_document(descriptions_from_file, f'{output_path}{basename}.desc')
                
            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {e}")
                
    # 接下来调用汇总函数
    # create_summary_document(all_descriptions, 'output_document.txt')
    
if __name__ == "__main__":
    run()
