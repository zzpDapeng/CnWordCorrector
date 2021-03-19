#!usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import numpy as np
import os
import time


class Corrector(object):

    def __init__(self, config):
        self.word_dict_path = config.word_dict_path
        self.word_dict = self._load_word_dict(self.word_dict_path)

    def _load_word_dict(self, path):
        word_freq = {}
        if not os.path.exists(path):
            # logger.warning('file not found: %s' % path)
            return word_freq
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split()
                if len(info) < 1:
                    continue
                word = info[0]
                # 取词频，默认1
                freq = int(info[1]) if len(info) > 1 else 1
                word_freq[word] = freq
        self.word_dict_path = path
        return word_freq

    def FMM(self, word_dict, token, window_size=5):
        idxs = []
        result = []
        index = 0
        text_size = len(token)
        while text_size > index:
            for size in range(window_size + index, index, -1):
                piece = token[index:size]
                if piece in word_dict:
                    index = size - 1
                    idxs.append(index - len(piece) + 1)
                    result.append(piece)
                    break
            index = index + 1
        return idxs, result

    def find_diff(self, detail):
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

    def details_calibration(self, details, text_new):
        max_word_len = 5
        # print(f"max_len: {max_len}")

        for_delete = []
        for i, detail in enumerate(details):
            # print(f"detail: {detail}")
            start_idx = (detail[3] - max_word_len) if (detail[3] - max_word_len) > 0 else 0
            end_idx = detail[3] + max_word_len
            # print(text_new[start_idx:end_idx])
            _, confuses = self.FMM(self.word_dict, text_new[start_idx:end_idx], max_word_len)
            confuses = [confuse for confuse in confuses if (len(confuse) >= 3 and detail[1] in confuse)]
            # print(f"confuses: {confuses}")
            if not confuses:
                for_delete.append(detail)
            else:
                details[i] = self.find_diff(detail)
        for detail in for_delete:
            details.remove(detail)
        return details

    def correct(self, corrected_sent, details):
        details = self.details_calibration(details, corrected_sent)
        return details
