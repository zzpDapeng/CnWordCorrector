# -*- coding: utf-8 -*-
# @Author  : Dapeng
# @File    : test.py
# @Desc    : 
# @Contact : zzp_dapeng@163.com
# @Time    : 2020/10/12 下午6:59
from pycorrector.bert.bert_corrector import BertCorrector

d = BertCorrector()
error_sentences = [
    '疝気医院那好 为老人让坐，疝気专科百科问答',
    '少先队员因该为老人让坐',
    '少 先  队 员 因 该 为 老人让坐',
    '机七学习是人工智能领遇最能体现智能的一个分知',
    '今天心情很好',
]
for sent in error_sentences:
    corrected_sent, err = d.bert_correct(sent)
    print("original sentence:{} => {}, err:{}".format(sent, corrected_sent, err))
