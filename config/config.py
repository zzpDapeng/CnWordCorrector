#!usr/bin/env python
# -*- coding:utf-8 -*-


class Config(object):
    confusion_path = "data/custom_confusion.txt"
    word_dict_path = "data/dict.txt"
    same_pinyin_path = "data/same_pinyin.txt"
    same_stroke_path = "data/same_stroke.txt"
    lm_model_path = "data/people_chars_lm.klm"
    char_set_path = "data/common_char_set.txt"
    pinyin2word_path = "data/pinyin2word.model"


config = Config()

if __name__ == '__main__':
    print(config.confusion_path)
