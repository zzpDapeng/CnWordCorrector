# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : data_preprocess.py
# @Desc    : 目录标题索引纠错
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/9/30 下午4:09
import json
import os
import difflib
from utils import pad

DIFF_SEPARATOR = ['  ，', '  ,', '  。', '  ；', '  ：']  # 句子分隔符：逗号,逗号(半角),句号,分号,冒号


def error(data_json):
    """
    目录标题索引错误纠错
    :param data_json: 原始json文件
    :return: 错误列表如：['3001010515167001,恢复', '3001011106067001,工业']
    """
    error_list = []
    error_with_delete = []
    if not os.path.exists(data_json):
        print('Json file not available')
        return None
    with open(data_json, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    for data in data_list:
        file_type = data.get('file_type')
        file_no = data.get('file_no')
        if file_type == '3':  # 只有第3类文章有目录
            catalogue_titles = data.get('catalogue_titles')
            subtitles = data.get('subtitles')
            assert len(catalogue_titles) == len(subtitles)
            for title_no in range(len(catalogue_titles)):
                paragraph_no = catalogue_titles[title_no].get('paragraph_no')
                sentence_start_no = int(catalogue_titles[title_no].get('sentence_start_no'))
                sentence_no = sentence_start_no
                catalogue_title_text = catalogue_titles[title_no].get('text')
                subtitle_text = subtitles[title_no].get('text')
                if '\n' in subtitle_text:
                    subtitle_text = subtitle_text.replace('\n', '')
                diff = difflib.Differ().compare(subtitle_text, catalogue_title_text)  # subtitle_text是正确的，作为参考在前面
                diff = list(diff)
                i = 0
                position = i
                while i < len(diff):
                    words = ''
                    error_label = diff[i][0]
                    word = diff[i][2]
                    if error_label == '+':  # 增加了字符（后面跟这-则表示修改了字符）
                        start_index = i - position + 1
                        end_index = start_index
                        words += word
                        while True and i < len(diff) - 1:
                            i += 1
                            next_error_label = diff[i][0]
                            next_word = diff[i][2]
                            if next_error_label == '+':
                                words += next_word
                                end_index += 1
                            elif next_error_label == ' ':
                                break
                        error_list.append(
                            file_type + file_no + paragraph_no + pad(sentence_no, 2) + pad(str(start_index), 2) +
                            pad(str(end_index), 2) + '7001,' + words)
                        error_with_delete.append(
                            file_type + file_no + paragraph_no + pad(sentence_no, 2) + pad(str(start_index), 2) +
                            pad(str(end_index), 2) + '7001,' + words)
                    elif error_label == '-':  # 删除、修改
                        start_index = i - position + 1
                        is_delete = True
                        change_num = 0
                        words += word
                        while i < len(diff) - 1:
                            i += 1
                            next_error_label = diff[i][0]
                            next_word = diff[i][2]
                            if next_error_label == '-':
                                words += next_word
                                continue
                            elif next_error_label == '+':  # 修改
                                is_delete = False
                                change_num += 1
                            elif next_error_label == ' ':
                                break
                        if is_delete:
                            end_index = start_index
                            error_with_delete.append(
                                file_type + file_no + paragraph_no + pad(sentence_no, 2) + pad(str(start_index), 2) +
                                pad(str(end_index), 2) + '7001,' + words+',1')
                        else:
                            end_index = start_index + change_num - 1
                            error_with_delete.append(
                                file_type + file_no + paragraph_no + pad(sentence_no, 2) + pad(str(start_index), 2) +
                                pad(str(end_index), 2) + '7001,' + words)
                        error_list.append(
                            file_type + file_no + paragraph_no + pad(sentence_no, 2) + pad(str(start_index), 2) +
                            pad(str(end_index), 2) + '7001,' + words)
                    elif diff[i] in DIFF_SEPARATOR:  # 标点分隔句子
                        sentence_no += 1
                        position = i + 1
                    i += 1
    return error_list, error_with_delete


if __name__ == '__main__':
    print(error('resources/data.json'))
