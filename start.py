# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : start.py
# @Desc    : 
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/10/12 11:09
import argparse
import os

from context_error import context_error
from docx_process.docx2json import docx_preprocess
from docx_process.label_docx import label_docx
from index_error import figure_error
from index_error import title_error
from noun_error.ProperNounError import proper_noun_error
from punc_error import punctuation
from word_error import sentences_error


def corrector(data_path):
    error_list = []
    error_list_for_label = []

    print('docx to json...')
    data_json = docx_preprocess(data_path)
    print('docx to json, complete:{}\n'.format(data_json))

    print('7_1-catalogue index error...')
    index_list, index_list_with_delete = title_error.error(data_json)
    error_list.extend(index_list)
    error_list_for_label.extend(index_list_with_delete)
    print('7_1-catalogue index error num:{}\n'.format(len(index_list)))
    print('7_2-figure index error...')
    figure_list, figure_list_with_delete = figure_error.error(data_json, data_path)
    error_list.extend(figure_list)
    error_list_for_label.extend(figure_list_with_delete)
    print('7-2-figure index error num: {}\n'.format(len(figure_list)))

    print('6-context error...')
    context_list = context_error.error(data_json)
    error_list.extend(context_list)
    error_list_for_label.extend(context_list)
    print('6-context error num:{}\n'.format(len(context_list)))

    print('2-punctuation error...')
    punctuation_list = punctuation.error(data_json)
    error_list.extend(punctuation_list)
    error_list_for_label.extend(punctuation_list)
    print('2-punctuation error num:{}\n'.format(len(punctuation_list)))

    print('1-word error...')
    sentences_list, error_detail = sentences_error.error(data_json)
    # error_list.extend(sentences_list)
    # error_list_for_label.extend(sentences_list)
    print('1-word error num:{}'.format(len(sentences_list)))

    print('4-noun error...')
    noun_list, word_error_list = proper_noun_error(error_detail)
    error_list.extend(noun_list)
    error_list_for_label.extend(noun_list)
    error_list.extend(word_error_list)
    error_list_for_label.extend(word_error_list)
    print('4-noun error num:{}\n'.format(len(noun_list)))

    # 置信度替换
    new_error_list = []
    for error in error_list:
        new_error = error[:13]+'99'+error[15:]
        new_error_list.append(new_error)
    error_list = new_error_list

    # 排序输出
    error_list.sort()
    error_list_for_label.sort()
    print('save result, generate labeled word')
    file_error = os.path.join(data_path, 'label.txt')
    file_error_with_delete = os.path.join(data_path, 'label_with_delete.txt')
    with open(file_error, 'w', encoding='utf-8') as f1, open(file_error_with_delete, 'w', encoding='utf-8') as f2:
        for i in range(len(error_list)):
            if i != len(error_list):
                f1.write(error_list[i] + '\n')
                f2.write(error_list_for_label[i] + '\n')
            else:
                f1.write(error_list[i])
                f2.write(error_list_for_label[i])
    label_docx(data_path, file_error_with_delete)


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-p', '--path', default='/media/dapeng/Documents/Competition/天智杯/科目4有标注', type=str,
                       help='data path')
    args = parse.parse_args()
    if args.path is None:
        print('please set data path')
    elif not os.path.exists(args.path):
        print('data path not available')
    else:
        corrector(args.path)
