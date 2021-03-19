import json
import os
from typing import List
from utils import pad

ERROR_CONSTANT = '2001,。'
DIFF_SEPARATOR = ['，', '。', '；', '：']  # 句子分隔符：逗号,句号,分号,冒号


def error(json_data_path: str) -> List[str]:
    """标点符号错误，句尾缺少句号

    标点符号错误，句尾缺少句号

    Args:
        json_data_path: json文件路径

    Returns:
        error_list：错误列表，如：['3001122012122001,。', '3001181713132001,。']

    """
    if not os.path.exists(json_data_path):
        print('Json not exist')
        return None

    with open(json_data_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    # print(data_list)
    error_list = []

    for data in data_list:
        file_type = data['file_type']
        file_no = data['file_no']
        sentences = data['sentences']
        for sentence in sentences:
            if sentence['type'] == '正文' and sentence['text'][-1] not in DIFF_SEPARATOR:
                # print(sentence)
                paragraph_no = sentence['paragraph_no']
                sentence_no = pad(sentence['sentence_no'], 2)
                start_index = pad(len(sentence['text']) + 1, 2)
                end_index = pad(len(sentence['text']) + 1, 2)
                error_list.append(file_type + file_no + paragraph_no + sentence_no + start_index + end_index + ERROR_CONSTANT)
    # print(error_list)
    return error_list


if __name__ == '__main__':
    error_list = error('data.json')
