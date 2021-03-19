from typing import List, Tuple

from config.config import config
from noun_error.corrector import Corrector
from utils import pad

ERROR_CONSTANT = '3001,'


def proper_noun_error(error_tuple: List[Tuple[str, str, List[List]]]):
    """专有名词错误

    Args:
        error_tuple: 字词错误返回的错误tuple，格式如下：
        [('1001010111111001,首', '8月中下旬京津冀区域首要污染物为臭氧', [['受', '首', 10, 11]]),
        ('1001020703031001,冀', '京津冀及周边、长三角和西北区域大部地区以良至轻度污染为主。', [['既', '冀', 2, 3]])]

    Returns:
        error_list: 专有名词错误列表(如：['1001020703033001,冀', '1001021001033001,驱逐舰'])
    """
    corrector = Corrector(config)
    error_list = []
    word_error = []

    for error_string, corrected_sent, details in error_tuple:
        # 进一步校准，从现有details中筛选出正向最长匹配成功的detail
        # print(details)
        details = corrector.details_calibration(details, corrected_sent)
        # print(details)
        if details:
            # 一句话对应多个错误的情况（如: [['家', '加', 1, 2], ['家', '加', 17, 18]]），所以循环
            for detail in details:
                # 判断错误结束位置索引是否匹配
                if error_string[10:12] == pad(detail[3], 2):
                    error_list.append(error_string[:12] + ERROR_CONSTANT + detail[1])
        else:
            word_error.append(error_string)

    return error_list, word_error


if __name__ == '__main__':
    a = [('1001010111111001,首', '8月中下旬京津冀区域首要污染物为臭氧', [['受', '首', 10, 11], ['氢', '氧', 17, 18]]),
         ('1001010118181001,氧', '8月中下旬京津冀区域首要污染物为臭氧', [['受', '首', 10, 11], ['氢', '氧', 17, 18]]),
         ('1001020703031001,冀', '京津冀及周边、长三角和西北区域大部地区以良至轻度污染为主。', [['既', '冀', 2, 3]]),
         ('2001051607071001,村', '建立山区生态村补偿机制，', [['林', '村', 6, 7]]),
         ('2001061007071001,第', '作为“棋盘”第一部分，', [['的', '第', 6, 7]]),
         ('2001061106061001,妻', '乃至一颗“妻子”，', [['棋', '妻', 5, 6]]),
         ('3001091907071001,低', '比1949年低8.3平方米增加了3.7倍。', [['的', '低', 6, 7]]),
         ('3001120107071001,林', '记者从农业农林部获悉知道，', [['村', '林', 6, 7]]),
         ('3001120309091001,给', '给华东5省（市）给东北部分地区水稻生产带来影响，', [['及', '给', 8, 9]]),
         ('3001122005051001,危', '“早霜”危害的风险增大', [['为', '危', 4, 5]]),
         ('3001180810101001,军', '国家邮政局副局长刘军表示：', [['君', '军', 9, 10]]),
         ('3001211411111001,识', '中国知道经济“新”意识足。', [['十', '识', 10, 11]]),
         ('1001010101031001,驱逐舰', '驱逐舰是一种通用的军舰哈哈驱逐舰', [['区主键', '驱逐舰', 0, 3], ['键', '舰', 15, 16]]),
         ('1001010116161001,舰', '驱逐舰是一种通用的军舰哈哈驱逐舰', [['区主键', '驱逐舰', 0, 3], ['键', '舰', 15, 16]])]

    proper_noun_error(a)
