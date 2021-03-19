# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : label_docx.py
# @Desc    : 根据docx文件和纠错文件label_with_delete.txt标注word文档
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/10/6 16:01
import os
import shutil
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.shared import Pt
from docx_process.docx2json import docx_to_paragraphs, get_paragraph_type, PUNCTUATION
from docx_process.docx2json import CATALOGUE_TITLE_FONT, SUBTITLE_FONT, BODY_FONT

FONT_DICT = {
    '目录标题': CATALOGUE_TITLE_FONT,
    '标题': SUBTITLE_FONT,
    '正文': BODY_FONT,
    '附图': BODY_FONT
}

FONT_SIZE_DICT = {
    '目录标题': 16,  # 三号
    '标题': 22,  # 二号
    '正文': 16,
    '附图': 16
}


def label_docx(data_path, label_txt, save_path=None):
    """
    根据原始word文档和纠错结果，生成标记后的word文档
    :param data_path: 无标注文本存放路径
    :param label_txt: 纠错标注文件
    :param save_path: docx文件保存路径，默认在data_path/label_docx目录下
    :return: None
    """
    # 初始化save_path
    if save_path is None:
        save_path = os.path.join(data_path, 'label_docx')
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
    os.mkdir(save_path)
    # 解析label_txt内容
    error_dict = {}
    if not os.path.exists(label_txt):
        print('label.txt not available')
        return None
    with open(label_txt, 'r', encoding='utf-8') as label_txt_file:
        lines = label_txt_file.readlines()
        if lines.__contains__('\n'):
            lines.remove('\n')
    for line in lines:
        parts = str(line).strip().split(',')
        label_code = parts[0]
        label_text = parts[1]
        is_delete = 0
        if len(parts) == 3:
            is_delete = parts[2]
            if int(is_delete) == 1:
                is_delete = 1
        file_no = str(label_code[:4])
        paragraph_no = str(label_code[4:6])
        sentence_no = str(label_code[6:8])
        start_index = str(label_code[8:10])
        end_index = str(label_code[10:12])
        error_dict.setdefault(file_no, []).append(
            {'paragraph_no': paragraph_no,
             'sentence_no': sentence_no,
             'start_index': start_index,
             'end_index': end_index,
             'text': label_text,
             'is_delete': is_delete})
    # 获取所有docx文件，并复制到save_path
    docx_list = []
    for file in os.listdir(data_path):
        if file.split('.')[-1] == 'docx':
            docx = os.path.join(data_path, file)
            save_docx = os.path.join(save_path, os.path.basename(docx))
            shutil.copyfile(docx, save_docx)
            docx_list.append(save_docx)
    # 处理复制后的docx
    for docx_file in docx_list:
        docx_name = os.path.basename(docx_file).split('.')[0]
        error_list = error_dict.get(docx_name)
        error_paragraph_list = []
        for error in error_list:
            error_paragraph_list.append(int(error.get('paragraph_no')))
        docx = Document(docx_file)
        paragraphs = docx_to_paragraphs(docx)
        for i in range(len(paragraphs)):
            paragraph_no = i + 1
            graph_list = paragraphs[i].get('paragraph')
            paragraph_type = get_paragraph_type(graph_list[0])
            # 如果该段落没有出错，则跳过
            if paragraph_no not in error_paragraph_list:
                continue
            # 段落出错，确定该段落中出错的句子。
            # 获取错误句子列表
            sentence_error_dict = {}
            for error in error_list:
                if int(error.get('paragraph_no')) == paragraph_no:
                    sentence_no = int(error.get('sentence_no'))
                    start_index = int(error.get('start_index'))
                    end_index = int(error.get('end_index'))
                    text = error.get('text')
                    is_delete = error.get('is_delete')
                    sentence_error_dict.setdefault(sentence_no, []).append((start_index, end_index, text, is_delete))
            # print(sentence_error_dict)  # {2: [(3, 3, '河')], 3: [(3, 3, '湖')]}
            sentence_error_list = sentence_error_dict.keys()
            sentence_no = 1
            for graph in graph_list:
                this_sentence_no = sentence_no
                error, sentence_no = check_graph(graph, sentence_no, sentence_error_list)
                if error:  # 定位到出错的graph
                    # 获取字体以设置style字体
                    if paragraph_type == '目录标签':
                        graph_type = get_paragraph_type(graph)
                    else:
                        graph_type = paragraph_type
                    # 纠错标记
                    label_graph(graph, graph_type, this_sentence_no, sentence_error_dict)
                else:
                    continue
        docx.save(docx_file)


def check_graph(graph, sentence_no, sentence_error_list):
    """
    检查该graph是否包含错误的句子
    :param graph: docx段落
    :param sentence_no: graph起始句子号
    :param sentence_error_list: 错误信息
    :return:
    """
    error = False
    sentences = []
    sentence = ''
    graph_text = graph.text.strip()
    start_no = sentence_no
    for word in graph_text:
        if word in PUNCTUATION:
            sentences.append(sentence)
            sentence = ''
        else:
            sentence += word
    if len(sentence) != 0:
        sentences.append(sentence)
    sentence_no_list = list(range(start_no, start_no + len(sentences)))
    for sentence_error_no in sentence_error_list:
        if sentence_error_no in sentence_no_list:
            error = True
    return error, start_no + len(sentences)


def label_graph(graph, graph_type, this_sentence_no, sentence_error_dict):
    """
    段落标记：将段落切分成句子
    :param graph:
    :param graph_type:
    :param this_sentence_no:
    :param sentence_error_dict:
    :return:
    """
    graph_text = graph.text
    sentence = ''
    sentence_no = this_sentence_no
    graph.clear()
    for word in graph_text:
        if word in PUNCTUATION:
            sentence += word
            graph = label_sentence(graph, sentence, sentence_no, graph_type, sentence_error_dict)
            sentence = ''
            sentence_no += 1
        else:
            sentence += word
    if len(sentence) != 0:
        label_sentence(graph, sentence, sentence_no, graph_type, sentence_error_dict)


def label_sentence(graph, sentence, sentence_no, graph_type, sentence_error_dict):
    """
    标记句子，首先判断句子是否需要标记，不需要标记则直接添加，需要标记则进行标记处理
    :param print_or_not:
    :param graph: 段落
    :param sentence_no: 句子号
    :param sentence_error_dict: 句子错误信息
    :param graph_type: 段落类型
    :param sentence: 句子内容
    :return:
    """
    font = FONT_DICT.get(graph_type)
    font_size = FONT_SIZE_DICT.get(graph_type)
    if sentence_no in sentence_error_dict.keys():  # 句子有错
        # 获取错误信息
        errors = sentence_error_dict.get(sentence_no)
        start_list = []
        end_list = []
        text_list = []
        is_delete = 0
        for error in errors:
            start_index, end_index, text, is_delete = error
            start_list.append(start_index)
            end_list.append(end_index)
            text_list.append(text)
            if is_delete:
                is_delete = 1
        # 根据错误位置标记子句
        if is_delete:
            add_text(graph, sentence, font, font_size, WD_COLOR_INDEX.YELLOW)
        else:
            sub_sentence = ''
            error_no = 0
            for i in range(len(sentence)):
                position = i + 1
                if position < start_list[error_no]:
                    sub_sentence += sentence[i]
                elif position == start_list[error_no] and position != end_list[error_no]:  # 开始结束位置不相同
                    add_text(graph, sub_sentence, font, font_size)
                    sub_sentence = sentence[i]
                elif position == start_list[error_no] and position == end_list[error_no]:  # 开始结束位置相同
                    # 加上无错的
                    add_text(graph, sub_sentence, font, font_size)
                    sub_sentence = sentence[i]
                    # 加上有错的
                    add_text(graph, sub_sentence, font, font_size, WD_COLOR_INDEX.YELLOW)
                    sub_sentence = ''
                    error_no += 1
                    if error_no >= len(start_list):
                        sub_sentence = sentence[end_list[error_no - 1]:]
                        break
                elif position < end_list[error_no]:
                    sub_sentence += sentence[i]
                elif position == end_list[error_no]:
                    sub_sentence += sentence[i]
                    add_text(graph, sub_sentence, font, font_size, WD_COLOR_INDEX.YELLOW)
                    error_no += 1
                    if error_no >= len(start_list):
                        sub_sentence = sentence[end_list[error_no - 1]:]
                        break
            if len(sub_sentence) > 0:
                add_text(graph, sub_sentence, font, font_size)
    else:  # 句子没错
        add_text(graph, sentence, font, font_size)
    return graph


def add_text(graph, text, font, font_size, color=None):
    """
    添加一个run（最小的文字单位）
    :param graph: docx段落
    :param text: 添加内容
    :param font: 字体样式
    :param font_size: 字体大小，单位Pt
    :param color: 强调颜色
    :return:
    """
    r = graph.add_run(text)
    r.font.highlight_color = color
    r.font.name = font
    r.font.size = Pt(font_size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), font)


if __name__ == '__main__':
    label_docx('/media/dapeng/Documents/Competition/天智杯/科目4无标注', '/media/dapeng/Documents/Competition/天智杯/科目4无标注/label_with_delete.txt')
