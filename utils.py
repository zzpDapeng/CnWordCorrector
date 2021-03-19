# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : sentences_error.py
# @Desc    : 
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/10/12 11:12
import numpy as np


def pad(num, max_len):
    """
    数字填充：
    For Example: 1 -> 01
    :param num: 数字
    :param max_len: 填充长度
    :return: 填充之后的字符串
    """
    num = str(num)
    num = num.zfill(max_len)
    return num


def find_diff(detail):
    array_a = np.array(list(detail[0]))
    array_b = np.array(list(detail[1]))
    diff_index = array_a != array_b
    diff = [i for i, index in enumerate(diff_index) if index]
    # print(diff)
    for i in range(len(diff) - 1):
        if diff[i] + 1 != diff[i + 1]:
            return detail

    start_index = detail[2] + diff[0]
    end_index = start_index + len(diff)

    new_detail = ["".join(list(array_a[diff])), "".join(list(array_b[diff])), start_index, end_index]
    return new_detail
