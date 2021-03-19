import difflib
import json
import re

# model mode
from pycorrector.bert.bert_corrector import BertCorrector

from utils import find_diff


# import pycorrector

def seg_char(sent):
    pattern = re.compile(r'([^A-Za-z0-9._-])')
    chars = pattern.split(sent)
    chars = [w for w in chars if len(w.strip()) > 0]
    return chars


DIFF_SEPARATOR = ['  ，', '  。', '  ；', '  ：']


def error(data_json):
    with open(data_json, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    # model mode
    d = BertCorrector()

    error_list = []
    error_detail = []
    for data in data_list:
        file_type = data.get('file_type')
        file_no = data.get('file_no')
        first_type = None
        first_no = None
        local_part = 0
        for s in data.get('sentences'):
            if s.get('type') == "正文" or (file_type != '3' and s.get('type') == '标题'):
                paragraph_no = s.get('paragraph_no')
                sentence_no = s.get('sentence_no')
                text = s.get('text')
                list_text = []

                if s.get('type') == '标题':
                    spilt_text = text.split("\n")
                    for item in spilt_text:
                        list_text.append(item)
                else:
                    list_text.append(text)

                for i, item in enumerate(list_text):
                    # model mode
                    corrected_sent, details = d.bert_correct(item)
                    # corrected_sent, details = pycorrector.correct(text)

                    if first_type != s.get('type') or first_no != paragraph_no:
                        local_part = 0
                        first_type = s.get('type')
                        first_no = paragraph_no

                    new_details = []
                    # details : ['七', '器', 1, 2]
                    for detail in details:
                        new_details.append(find_diff(detail))
                        orign = detail[0]
                        fix = detail[1]
                        ds = difflib.SequenceMatcher(None, orign, fix)
                        for tag, i1, i2, j1, j2 in ds.get_opcodes():
                            if tag == 'replace':
                                part_text_1 = item[:detail[2] + i1 + 1]
                                part_text_2 = item[:detail[2] + i2 + 1]
                                add_1 = seg_char(part_text_1)
                                add_2 = seg_char(part_text_2)
                                error = '%s%s%s%s%s%s1,%s' % (file_type,
                                                              file_no,
                                                              str(int(paragraph_no) + i).zfill(2),
                                                              str(len(add_1) + local_part).zfill(3),
                                                              # str(detail[2] + 1 + i1 + local_part).zfill(3),
                                                              str(int(paragraph_no) + i).zfill(2),
                                                              str(len(add_2) - 1 + local_part).zfill(3),
                                                              # str(detail[2] + i2 + local_part).zfill(3),
                                                              fix[j1:j2]
                                                              )
                                error_list.append(error)
                                error_detail.append((error, corrected_sent, new_details))
    return error_list, error_detail


if __name__ == '__main__':
    error_list, error_detail = error('/media/dapeng/Documents/Code/PyCharmProjects/NLPCorrector/data/data.json')
    print(error_detail)
    print("Over")
