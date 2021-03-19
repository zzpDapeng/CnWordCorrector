# -*- coding: utf-8 -*-
# @Author  : Dapeng
# @File    : figure_error.py
# @Desc    : 
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/10/12 下午5:39
import difflib
import json
import re

import cv2
from paddleocr import PaddleOCR

DIFF_SEPARATOR = ['  ，', '  。', '  ；', '  ：']


def half2full(s):
    n = ''
    for char in s:
        num = ord(char)
        if (num == 32):  # 半角空格转成全角
            num = 0x3000
        elif 33 <= num <= 126:
            num += 65248  # 16进制为0xFEE0
        num = chr(num)
        n += num
    return n


def error(data_json, files_path):
    # 初始化ocr
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    with open(data_json, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    error_list = []
    insert_mark = []
    for data in data_list:
        file_type = data.get('file_type')
        file_no = data.get('file_no')
        figures = data.get('figures')
        if len(figures) == 0:
            break

        for i, figure in enumerate(figures):
            # 确定图片文件名以及路径
            figure_name = '%s%s-%s.jpg' % (file_type, file_no, str(i + 1))
            figure_path = '%s/%s' % (files_path, figure_name)
            # 裁剪图片,只保留标题部分
            I = cv2.imread(figure_path, flags=1)
            cropped = I[0:180]
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            # ocr识别
            result = ocr.ocr(cropped, cls=True)
            ocr_text = []
            # 处理文字识别结果
            # [[[24.0, 36.0], [304.0, 34.0], [304.0, 72.0], [24.0, 74.0]], ['纯臻营养护发素', 0.964739]]
            for line in result:
                ocr_text.append(line[-1][0])
            # 将识别结果拼接,去除掉第一项,因为第一项可能是"附图","附图一",这种没用的文字
            ocr_text = ''.join(ocr_text[1:])
            # 半角转全角,防止识别出的符号不是全角的
            ocr_text = half2full(ocr_text)
            # 记录下句子序号
            sentence_num = [0] * (len(ocr_text) + 1)
            for m, char in enumerate(ocr_text):
                if char in DIFF_SEPARATOR:
                    sentence_num[m] = sentence_num[m - 1] + 1

            sentence_num = sentence_num[1:]

            figure_text = figure.get('text')
            add_idx = 0
            # 删除文字前面数字序号的影响
            # 例如: 1.中国地图
            # 其中1.不需要考虑,但是位置需要保留
            idx = re.match(r'\d*\.', figure_text)
            if idx is not None:
                idx = idx.group()
                figure_text = figure_text[len(idx):]
                add_idx = len(idx)
            # 比对ocr结果与文中内容的差异
            s = difflib.SequenceMatcher(None, figure_text, ocr_text)
            for tag, i1, i2, j1, j2 in s.get_opcodes():
                paragraph_no = figure.get('paragraph_no')
                sentence_start_no = int(figure.get('sentence_start_no'))
                if tag is 'replace':
                    error = '%s%s%s%s%s%s7001,%s' % (file_type,
                                                     file_no,
                                                     paragraph_no,
                                                     str(sentence_start_no + sentence_num[i1]).zfill(2),
                                                     str(i1 + 1).zfill(2) if add_idx is None else str(
                                                         i1 + 1 + add_idx).zfill(2),
                                                     str(i2).zfill(2) if add_idx is None else str(i2 + add_idx).zfill(
                                                         2),
                                                     ocr_text[j1:j2]
                                                     )

                    error_list.append(error)
                    insert_mark.append(error)

                elif tag is 'delete':
                    error = '%s%s%s%s%s%s7001,%s' % (file_type,
                                                     file_no,
                                                     paragraph_no,
                                                     str(sentence_start_no + sentence_num[i1]).zfill(2),
                                                     str(i1 + 1).zfill(2) if add_idx is None else str(
                                                         i1 + 1 + add_idx).zfill(2),
                                                     str(i2).zfill(2) if add_idx is None else str(i2 + add_idx).zfill(
                                                         2),
                                                     figure_text[i1:i2]
                                                     )
                    error_list.append(error)
                    insert_mark.append(error)

                elif tag is 'insert':
                    error = '%s%s%s%s%s%s7001,%s' % (file_type,
                                                     file_no,
                                                     paragraph_no,
                                                     str(sentence_start_no + sentence_num[i1]).zfill(2),
                                                     str(i1 + 1).zfill(2) if add_idx is None else str(
                                                         i1 + 1 + add_idx).zfill(2),
                                                     str(i2 + 1).zfill(2) if add_idx is None else str(
                                                         i2 + 1 + add_idx).zfill(2),
                                                     figure_text[i1:i2]
                                                     )
                    error_mark = 'error,1' % (error)
                    error_list.append(error)
                    insert_mark.append(error_mark)
    return error_list, insert_mark
