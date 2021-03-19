import difflib
import json

# model mode
from pycorrector.bert.bert_corrector import BertCorrector
# import pycorrector

from utils import find_diff

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
        for s in data.get('sentences'):
            if s.get('type') == "正文" or (file_type != '3' and s.get('type') == '标题'):
                paragraph_no = s.get('paragraph_no')
                sentence_no = s.get('sentence_no')
                text = s.get('text')

                # model mode
                corrected_sent, details = d.bert_correct(text)
                # corrected_sent, details = pycorrector.correct(text)

                new_details = []
                # details : ['七', '器', 1, 2]
                for detail in details:
                    new_details.append(find_diff(detail))
                    orign = detail[0]
                    fix = detail[1]
                    s = difflib.SequenceMatcher(None, orign, fix)
                    for tag, i1, i2, j1, j2 in s.get_opcodes():
                        if tag == 'replace':
                            error = '%s%s%s%s%s%s1001,%s' % (file_type,
                                                             file_no,
                                                             paragraph_no,
                                                             sentence_no,
                                                             str(detail[2] + 1 + i1).zfill(2),
                                                             str(detail[2] + i2).zfill(2),
                                                             fix[j1:j2]
                                                             )
                            error_list.append(error)
                            error_detail.append((error, corrected_sent, new_details))
    return error_list, error_detail
