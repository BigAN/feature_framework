#!/usr/env/bin python
# coding=utf8
import re

__author__ = 'zhuliang'


def split_line(line):
    """
    以半角逗号为分隔符，切分一行文本
    '\,' 作为文本中逗号的转义
    """
    splited = re.split(r'(?<!\\),', line)

    def _parse(one):
        return re.sub(r'\\,', ',', one.strip())

    mapped = map(_parse, splited)
    return mapped

    # 日志允许有空列，所以这段逻辑去掉
    #def _filter_bad(one):
    #    return bool(one)

    #filtered = filter(_filter_bad, mapped)

    #if len(filtered) < len(mapped):
    #    raise Exception("bad row. something has been filtered.")
    #return filtered