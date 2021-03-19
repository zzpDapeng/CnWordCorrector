# -*- coding: utf-8 -*-
# @Author  : Zhipeng Zhang
# @File    : docx2json.py
# @Desc    : 天智杯doc/docx文件预处理
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/9/28 下午7:48
from docx import Document
from utils import pad
import json
import os

# Word参数, 文章内容依据字体来判断，字体大小没有用到
CATALOGUE_LABEL_FONT = '楷体_GB2312'  # 目录标签字体
CATALOGUE_LABEL_SIZE = 228600  # 目录标签大小，18号，即小二，对于其他字号，换算关系：Pt=12700*字号，如：228600=12700*18
CATALOGUE_TITLE_FONT = '黑体'  # 目录标题字体
CATALOGUE_TITLE_SIZE = None  # 目录标题字体大小
SUBTITLE_FONT = '方正小标宋简体'  # 小标题字体
SUBTITLE_SIZE = 279400  # 小标题字体大小,单位Pt,279400代表22号字体大小（即二号）
BODY_FONT = '仿宋_GB2312'  # 正文、附录字体
BODY_SIZE = None  # 不能获得正文字体大小

PUNCTUATION = ['，', ',', '。', '；', '：']  # 句子分隔符：逗号,句号,分号,冒号
FIGURE_LABEL = ['附图', '附件']  # 附图标志
TYPE = ['目录标签', '目录标题', '标题', '正文', '附图']  # 文章内容类型


def docx_preprocess(data_path):
    """
    实现docx数据预处理，生成json文件，json格式说明见“Doc/Docx文件预处理.md”
    TODO：首先在windows环境下使用doc2docx.py的doc2docx(数据目录)将doc批量转换为docx文件
    :param data_path: 数据保存路径（绝对路径）
    :return: 无，生成data.json, 默认存储在data_path目录下
    """
    # 遍历路径，获得所有.doc和.docx文件
    docx_list = []
    json_file_list = []
    for file in os.listdir(data_path):
        if file.endswith('.docx'):
            file = os.path.join(data_path, file)
            docx_list.append(file)
    for docx_file in docx_list:
        docx = Document(docx_file)
        file_name = os.path.basename(docx_file).split('.')[0]  # 文件名（前4位），如1001
        file_type = file_name[0]  # 产品类型（1位）1,2,3
        file_no = file_name[1:]  # 文本编号（3位）
        sentences = []
        paragraphs = docx_to_paragraphs(docx)
        graph_no = 1
        for paragraph_dict in paragraphs:
            graph_list = paragraph_dict.get('paragraph')
            graph_type = paragraph_dict.get('type')
            graph_sentences = paragraph_to_sentences(graph_list, graph_no, graph_type)
            for sentence in graph_sentences:
                sentences.append(sentence)
            graph_no += 1
        # 根据句子（sentences）生成目录标题（catalogue_titles）、小标题（subtitles）、正文段落（figures）、附图（figures）
        catalogue_titles = get_catalogue_title(sentences)
        subtitles = get_subtitle(sentences)
        paragraphs = get_paragraphs(sentences)
        figures = get_figures(sentences)
        # 打包到json
        file_dict = {
            "file_type": file_type,
            "file_no": file_no,
            "sentences": sentences,
            "catalogue_titles": catalogue_titles,
            "subtitles": subtitles,
            "paragraphs": paragraphs,
            "figures": figures
        }
        json_file_list.append(file_dict)
    # 写入data.json文件
    json_file = os.path.join(data_path, 'data.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_file_list, f, ensure_ascii=False, indent=2)
    return str(json_file)


def get_paragraph_type(graph):
    """
    获取一个原始graph的格式
    :param graph: docx.graph对象
    :return: str类型,TYPE中的一个类型
    """
    font = ''
    text = ''
    runs = graph.runs
    for run in runs:
        font = run.font.name
        text = run.text
        break
    if font == CATALOGUE_LABEL_FONT:
        return TYPE[0]  # 目录标签
    elif font == CATALOGUE_TITLE_FONT:
        return TYPE[1]  # 目录标题
    elif font == SUBTITLE_FONT:
        return TYPE[2]  # 小标题
    elif font == BODY_FONT:  # 正文或附件、附图
        figure = False
        for figure_label in FIGURE_LABEL:
            if text.startswith(figure_label):
                figure = True
        if not figure:
            return TYPE[3]
        else:
            return TYPE[4]
    else:
        print('未知的字体类型，请检查Word参数设置与实际Word中的字体是否匹配')
        return None


def docx_to_paragraphs(docx):
    """
    获取docx文件的段落graphs信息（不含空行信息）
    :param docx: Document格式的docx文件
    :return: 段落信息列表，列表内存储字典，字典包含键graph和键type. For example:
            [{'paragraph': [<docx.text.paragraph.Paragraph object at 0x0000021C4BD5A7B8>], 'type': '标题'},
            {'paragraph': [<docx.text.paragraph.Paragraph object at 0x0000021C4BD5A898>], 'type': '正文'},
            {'paragraph': [<docx.text.paragraph.Paragraph object at 0x0000021C4BD5A978>], 'type': '附图'}]
    """
    docx_paragraph_list = []
    graphs = docx.paragraphs
    graph_list = []
    i = 0
    while i < len(graphs):
        graph = graphs[i]
        text = graph.text
        if text != '':
            graph_type = get_paragraph_type(graph)
            if graph_type == TYPE[0]:  # 目录标签
                graph_list.append(graph)
                i += 1
                next_type = get_paragraph_type(graphs[i])
                while next_type == TYPE[0] or next_type == TYPE[1]:
                    graph_list.append(graphs[i])
                    i += 1
                    if i >= len(graphs):
                        break
                    next_type = get_paragraph_type(graphs[i])
                i -= 1
                docx_paragraph_list.append({"paragraph": graph_list, "type": graph_type})
                graph_list = []
            elif graph_type == TYPE[2]:  # 小标题
                graph_list.append(graph)
                i += 1
                next_text = graphs[i].text
                while next_text.strip() != '':
                    graph_list.append(graphs[i])
                    i += 1
                    if i >= len(graphs):
                        break
                    next_text = graphs[i].text
                i -= 1
                docx_paragraph_list.append({"paragraph": graph_list, "type": graph_type})
                graph_list = []
            elif graph_type == TYPE[4]:  # 附图
                graph_list.append(graph)
                i += 1
                while graphs[i].text.strip() != '':
                    graph_list.append(graphs[i])
                    i += 1
                    if i >= len(graphs):
                        break
                i -= 1
                docx_paragraph_list.append({"paragraph": graph_list, "type": graph_type})
                graph_list = []
            else:  # 正文
                graph_list.append(graph)
                docx_paragraph_list.append({"paragraph": graph_list, "type": graph_type})
                graph_list = []
        i += 1
    return docx_paragraph_list


def paragraph_to_sentences(graph_list, graph_no, paragraph_type=None):
    """
    将一个段落解析成句子
    :param graph_no: 段落号
    :param graph_list: 一个段落（一个段落里可能包含多个原始段落graph）
    :param paragraph_type: 段落类型
    :return:
    """
    sentences = []
    sentence = ''
    sentence_no = 1
    if paragraph_type == TYPE[0]:  # 目录分句。目录段需要解析出两种类型
        for graph in graph_list:
            paragraph_type = get_paragraph_type(graph)
            if paragraph_type == TYPE[0]:  # 目录标签， 直接添加
                sentences.append({"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), 'type': TYPE[0],
                                  "text": graph.text.strip()})
                sentence_no += 1
            elif paragraph_type == TYPE[1]:  # 目录标题， 需断句再添加。
                for word in graph.text:  # 断句
                    sentence += word
                    if word in PUNCTUATION:
                        sentences.append(
                            {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), 'type': TYPE[1],
                             "text": sentence.strip()})
                        sentence_no += 1
                        sentence = ''
                if sentence != '':  # 不以标点结束的句子
                    sentences.append(
                        {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[1],
                         "text": sentence.strip()})
                    sentence = ''
                    sentence_no += 1
    elif paragraph_type == TYPE[2]:  # 小标题分句
        for graph in graph_list:
            for word in graph.text:  # 断句
                sentence += word
                if word in PUNCTUATION:
                    sentences.append(
                        {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[2],
                         "text": sentence.strip()})
                    sentence = ''
                    sentence_no += 1
            if sentence != '':  # 不以标点结束的句子
                sentences.append({"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[2],
                                  "text": sentence.strip()})
                sentence_no += 1
                sentence = ''
    elif paragraph_type == TYPE[3]:  # 正文分句。正文段均独立成段
        assert len(graph_list) == 1
        for word in graph_list[0].text:  # 断句
            sentence += word
            if word in PUNCTUATION:
                sentences.append({"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[3],
                                  "text": sentence.strip()})
                sentence = ''
                sentence_no += 1
        if sentence != '':  # 不以标点结束的句子
            sentences.append(
                {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[3],
                 "text": sentence.strip()})
            sentence_no += 1
    elif paragraph_type == TYPE[4]:  # 处理附录段。说明：每个附录段的第一个句子是"附件：/附图：",处理时忽略掉附录段的第一个句子
        for graph in graph_list:
            for word in graph.text:  # 先处理附录第一行，断句
                sentence += word
                if word in PUNCTUATION:
                    sentences.append(
                        {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[4],
                         "text": sentence.strip()})
                    sentence = ''
                    sentence_no += 1
            if sentence != '':  # 不以标点结束的句子
                sentences.append(
                    {"paragraph_no": pad(graph_no, 2), "sentence_no": pad(sentence_no, 2), "type": TYPE[4],
                     "text": sentence.strip()})
                sentence = ''
                sentence_no += 1
    return sentences


def get_catalogue_title(sentences):
    """
    根据sentences列表获取目录标题
    合并问题：①对于标题中因含有标点符号而被切分的句子，需要将其合并，因此一个标题可能含有多个句子，用sentence_start_no标记该标题中的第一句序号
    :param sentences: 句子列表
    :return: 目录标题列表
    """
    catalogue_titles = []
    i = 0
    while i < len(sentences):
        sentence_type = sentences[i].get('type')
        if sentence_type == TYPE[1]:
            text = sentences[i].get('text')
            start_no = sentences[i].get('sentence_no')
            while text[-1] in PUNCTUATION:  # 合并因标点符号切分的目录标题
                i += 1
                text += sentences[i].get('text')  # 假设：目录标题不会以4种标点符号结尾
            title = {
                "paragraph_no": sentences[i].get('paragraph_no'),
                "sentence_start_no": start_no,
                "text": text
            }
            catalogue_titles.append(title)
        i += 1
    return catalogue_titles


def get_subtitle(sentences):
    """
    获取小标题
    合并问题：在get_catalogue_title合并标点问题①的基础上还要解决合并换行问题。返回结果中如遇到标题中有\n，则该位置要断句
    小标题自成一段，因此句子起始号始终为01，所以不加入sentence_start_no字段
    For Example:
    “中宣部、公安部部署开展“最美基层民警”\n学习宣传活动”中包含两句：“中宣部、公安部部署开展“最美基层民警””、“学习宣传活动”
    :param sentences:
    :return:
    """
    subtitles = []
    i = 0
    while i < len(sentences):
        sentence_type = sentences[i].get('type')
        if sentence_type == TYPE[2]:
            text = sentences[i].get('text')
            while True:
                i += 1
                next_type = sentences[i].get('type')
                if next_type == TYPE[2] and text[-1] not in PUNCTUATION:  # 合并因为换行(最后无标点)而分句的标题
                    text += '\n' + sentences[i].get('text')
                elif text[-1] in PUNCTUATION:  # 合并因标点符号切分的目录标题（即便标点符号在行结尾也没关系，都是要加一句）
                    text += sentences[i].get('text')  # 假设：标题不会以4种标点符号结尾
                else:
                    i -= 1
                    break
            title = {
                "paragraph_no": sentences[i].get('paragraph_no'),
                "text": text
            }
            subtitles.append(title)
        i += 1
    return subtitles


def get_figures(sentences):
    """
    获取附图/附件
    生成结果以句子为单位，同样考虑了标点合并问题①，此外还过滤了“附图：”“附件：”等不需要进行索引纠错的句子
    TODO: 有的句子包含序号，有的不包含序号如“1.湖北省邯郸市（局部）卫星影像图”、“求是杂志发表习近平总书记重要文章示意图”，纠错时需要判断
    :param sentences: 句子列表
    :return:  附图/附件列表
    """
    figures = []
    i = 0
    while i < len(sentences):
        sentence_type = sentences[i].get('type')
        if sentence_type == TYPE[4]:
            text = sentences[i].get('text')
            is_figure_label = False
            for figure_label in FIGURE_LABEL:
                if text.startswith(figure_label):
                    is_figure_label = True
            if is_figure_label:
                i += 1
                continue
            start_no = sentences[i].get('sentence_no')
            while text[-1] in PUNCTUATION:  # 合并因标点符号切分的附图
                i += 1
                text += sentences[i].get('text')  # 假设：附图不会以4种标点符号结尾
            figure = {
                "paragraph_no": sentences[i].get('paragraph_no'),
                "sentence_start_no": start_no,
                "text": text
            }
            figures.append(figure)
        i += 1
    return figures


def get_paragraphs(sentences):
    """
    获取正文段落，正文均独立成段，因此不含sentence_start_no字段
    :param sentences: 句子列表
    :return: 正文段落列表，
    """
    paragraphs = []
    i = 0
    while i < len(sentences):
        sentence_type = sentences[i].get('type')
        if sentence_type == TYPE[3]:
            text = sentences[i].get('text')
            paragraph_no = sentences[i].get('paragraph_no')
            while True:
                i += 1
                next_type = sentences[i].get('type')
                next_paragraph_no = sentences[i].get('paragraph_no')
                if next_type != TYPE[3]:  # 正文结束
                    i -= 1
                    break
                if next_paragraph_no != paragraph_no:  # 正文没有结束但另起一段
                    i -= 1
                    break
                text += sentences[i].get('text')
            paragraph = {
                "paragraph_no": paragraph_no,
                "text": text
            }
            paragraphs.append(paragraph)
        i += 1
    return paragraphs


if __name__ == '__main__':
    # 生成json文件
    docx_preprocess('E:\\Competition\\天智杯\\科目4无标注')
