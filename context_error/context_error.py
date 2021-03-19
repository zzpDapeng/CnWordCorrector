# coding=utf-8
import json
import re

dic = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7}
PUNCTUATION = ['，', ',', '。', '；', '：']
pattern = re.compile(r"[一二三四五六七八九][是个要方]")


def error(data_json):
    code = []
    with open(data_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    for article in json_data:
        file_type = article.get('file_type')
        file_no = article.get('file_no')
        for ele in article['paragraphs']:
            paragraph_no = ele.get('paragraph_no')
            text = ele['text']
            if pattern.findall(ele['text']):
                ilist = pattern.findall(ele['text'])
                if dic[ilist[0][0]] > 1 and dic[ilist[0][0]] != dic[ilist[-1][0]]:
                    error_word = ilist[0][0]
                    correct_word = ilist[-1][0]
                    # print('error_word', error_word)
                    # print('corrector:', correct_word)
                    # print(text)
                    sentence_no = 0
                    start = 0
                    sentence = ''
                    for word in text:
                        sentence += word
                        # if sentence[start - 1] + sentence[start] == error_word:
                        if sentence[start - 1] == error_word and sentence[start - 1] in ilist[0]:
                            end = convert(start)
                            result = file_type + file_no + paragraph_no + convert(sentence_no + 1) + convert(
                                start) + end + str(6001) + ',' + correct_word
                            # print(file_type+file_no+paragraph_no+convert(sentence_no+1)+convert(start)+end+str(6001)+'，'+correct_word)
                            code.append(result)

                        start += 1
                        if word in PUNCTUATION:
                            sentence_no += 1
                            # print(sentence_no, sentence)
                            start = 0
                            sentence = ''
    return code


def convert(digit):
    if digit >= 10:
        return str(digit)
    else:
        return '0' + str(digit)


if __name__ == '__main__':
    Data_Path = 'resources/data.json'
    # 3  001 12  04  06  06  6  00  1, 三
    print(error(Data_Path))
