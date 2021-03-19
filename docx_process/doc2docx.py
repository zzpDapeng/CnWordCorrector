# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : doc2docx.py
# @Desc    : 批量doc转docx
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/9/28 下午8:42
import os
from win32com import client  # 导入doc转换模块
import argparse


def doc2docx(data_path):
    word = client.Dispatch('Word.Application')  # 打开word应用程序
    docx_list = []
    for file in os.listdir(data_path):
        if file.endswith('.doc'):
            docx_list.append(file)
            file = os.path.join(data_path, file)
            doc = word.Documents.Open(file)  # 打开word文件
            doc.SaveAs("{}x".format(file), 12)  # 另存为后缀为".docx"的文件，其中参数12指docx文件
            doc.Close()  # 关闭原来word文件
    word.Quit()
    print('doc转换docx已完成，共转换{}个doc文件'.format(len(docx_list)))
    return len(docx_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=None, type=str, help='data path')
    args = parser.parse_args()
    if args.path is None:
        print('请指定数据路径')
    elif not os.path.exists(args.path):
        print('数据路径不存在')
    else:
        doc2docx(args.path)
