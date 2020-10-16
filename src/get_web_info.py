import os, sys

"""
本脚本用于：解析360浏览器收藏夹导出来的HTML文件
"""

# TODO 安装解析包
# # Beautiful Soup
# pip install bs4
#
# # 解析器
# pip install lxml
# pip install html5lib

# TODO 初始化soup
# 初始化
# from bs4 import BeautifulSoup

# 方法一，直接打开文件
web_source_file = "../source/Web-Source.html"
# os.chdir("source")
# print(sys.argv[0])
# soup = BeautifulSoup(open(web_source_file, encoding='utf-8'))

# 方法二，指定数据
# resp = "<html>data</html>"
# soup = BeautifulSoup(resp, 'lxml')

# soup 为 BeautifulSoup 类型对象
# print(type(soup))

# TODO 查找
# soup.text
# soup.find_all("H3")

# TODO 换正则匹配
import re

file_web_md = "../source/web-source.md"
# 清空要写入的文件
with open(file_web_md, "w") as fw:
    fw.truncate()

with open(web_source_file, encoding='utf-8') as f:
    line = f.readline()
    while line:
        # 处理line
        # print(line)
        res = re.search("H3 .*>(.*)</H3>", line)
        if res:
            title = res.group(1)
            print(title)
            with open(file_web_md, "a") as fw:
                fw.write("### " + title + "\n")
            # 下一行
        res = re.search('<DT><A HREF=\"(.*?)\".*>(.*?)</A>', line)
        if res:
            link = res.group(1)
            link_name = res.group(2)
            print(link_name, ":\t\t", link)
            with open(file_web_md, "a") as fw:
                try:
                    md_text = f"- [{link_name}]({link})\n"
                    fw.write(md_text)
                except Exception as e:
                    print(repr(e))
                    # 字符串编码转换
                    # "中".encode('unicode-escape') # 中文转为16进制的Unicode编码 b'\\u4e2d'
                    # b'\u4e2d'.decode('unicode-escape')  # Unicode的十六进制码转为汉字 '中'
                    # '❤'.encode('unicode-escape')  # 表情符号转为16进制的Unicode编码：b'\\u2764'
                    # b'\\u2764'.decode('unicode-escape') # Unicode的十六进制码转为表情符号：'❤'
                    # 参考Unicode编码列表：https://www.cnblogs.com/tinaluo/p/8098826.html
                    # 可以看到，从2580到2BFF，都是特殊符号，最好一并去掉
                    # 替换掉表情符号
                    link_name = re.sub(u"[\U00010000-\U0010ffff]", '', link_name)
                    link_name = re.sub(u"[\u2580-\u2bff]", '', link_name)
                    link_name = re.sub(u"[\uFE00-\uFE0F]", '', link_name)
                    link_name = re.sub(u"[\u00A0-\u00FF]", '', link_name)
                    link_name = re.sub(u"[\u2100-\u214f]", '', link_name)
                    md_text = f"- [{link_name}]({link})\n"
                    fw.write(md_text)
        line = f.readline()
s = '😮'
s.encode('unicode-escape')
b'\ufe0f'.decode('unicode-escape')
re.sub(u"[\U00010000-\U0010ffff]", '', s)
re.sub(u"[\u2580-\u2bff]", '', s)
re.sub(u"[\uFE00-\uFE0F]", '', s)
