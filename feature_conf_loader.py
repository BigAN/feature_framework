#!/usr/env/bin python
# coding=utf8

"""
单机版

对确定格式的日志文件，用一个配置文件定义以下内容：
1. 每列数据项的的含义
2. 定义由原始数据项生成高级特征、组合特征的生成函数（包括常用的和自定义的）

配置文件中可以用 # 作为注释。被注释的和空白行，都是无效行

第一个有效行定义输入数据的数据项含义。由半角逗号作为分隔符，逗号前后可以有空白符；
数据项中出现了半角逗号的需要用反斜杠转义（推荐不在数据项中再使用半角逗号）;例如：
uid,gid,show,clk,city,keyword

之后的有效行定义特征数据的生成方式，例如：
feature_name=user_id; slot=a; depend=uid; method=direct;
feature_name=keyword_splits; slot=c; depend=keyword; method=term_split; args=4
feature_name=user_id-group_id; depend=uid, gid; method=combine;

解释：
column_name后⾯面的字段依次对应原始⽇日志的每⼀一列，为后续特征列表的依赖项。
每个具体要抽取的特征会占据⼀一⾏行，包括feature_name, slot, depend, method, args（可
选）五项：
• feature_name为内部特征名字
• slot为特征分组名，既可以是数字（便于分析⽤用），也可以是字符（⽐比如给vw⽤用）
• depend指定特征抽取以来字段，这个depend既可以是原始⽇日志字段别名，也可以是之前抽取出来的特征。
• method是具体的特征抽取⽅方法，⼀一些⽐比较通⽤用的特征有：
        • direct: 直接输出
        • combine: 叉乘组合特征
        • term_split: 直接空格切分分词或者
• args是可选的参数，⽐比如举个例⼦子在term_split中args=4， 表⽰示做多输出4个切词term。这⾥里是举例，args完全是⾃自定义的

"""
import re
import codecs
import logging
import collections
import importlib

import predefined_methods as pm
import format_utils

import json


feature_definition_keys = set(['feature_name', 'label_name',
                               'slot', 'depend', 'method', 'args'])
custom_module = None
feature_index_dict = {}


def process(feature_conf_file, feature_data, output_file_path, output_format, feature_index_file=None):
    feature_extractors, columns = load_feature_conf(feature_conf_file)

    # 原始特征值
    with codecs.open(feature_data, 'r', 'utf8') as fin, \
            codecs.open(output_file_path, 'w', 'utf8') as fout:
        while True:
            line = fin.readline()
            if not line:
                break
            try:
                feature_line = parse_train_data(line, feature_extractors, columns, output_format)
                fout.write(feature_line)
                fout.write('\n')
            except:
                logging.exception('parsing one line error. line=%s' % line)

    if output_format == 'liblinear' and feature_index_file:
        save_feature_index(feature_index_file, feature_index_dict)


def save_feature_index(file, dict):
    """
    保存特征序列化字典
    :param file:
    :return:
    """
    global feature_index_dict
    with codecs.open(file, 'w', 'utf8') as fin:
        json.dump(dict, fin)


def load_feature_index(file):
    """
    加载序列化的特征字典
    :param file:
    :return:
    """
    global feature_index_dict
    with codecs.open(file, 'r', 'utf8') as fin:
        feature_index_dict = json.load(fin)


def load_feature_conf(feature_conf_file):
    def is_used_line(line):
        return (not re.match(r'^\s*#.*$', line)) and \
               (not re.match(r'^\s*$', line))

    with codecs.open(feature_conf_file, 'r', 'utf8') as f:
        lines = filter(is_used_line, f.readlines())
        if len(lines) < 1:
            raise Exception("too less lines in the conf file")

    line_number = 0
    # 第一行是输入文件格式定义
    columns = format_utils.split_line(lines[line_number])
    column_dict = {v: i for i, v in enumerate(columns)}
    line_number += 1

    # 第二行是自定义特征抽取工具类的路径
    m = re.match(r'^\s*custom_code_module\s*=\s*([.\w]*)\s*$', lines[line_number])
    if m:
        global custom_module
        custom_module = importlib.import_module(m.group(1))
        line_number += 1

    # 以下每行都是一个特征的生成定义
    feature_extractors = [one_feature(line, column_dict) for line in lines[line_number:]]
    # by Nevor
    # 增加返回数据的列数，用以判断日志的列数是否相同，因为之前出现了日志列数不一致的情况，导致解析出错
    # 列数不一致，说明特征配置和日志不匹配，需要重新协商
    return feature_extractors, len(columns)


def one_feature(line, column_dict):
    """
    :param line: 特征 or label 生成的定义
    :param column_dict: 数据项名称 -> 数据项所在列的列数
    :return: 返回一个函数
        这个函数接收按逗号分隔符split之后的数组，返回一个迭代器，每次yield出一个特征
    """
    define_pattern = r'([a-zA-Z][^=]*)\s*=\s*(\S[^;]*)'
    dd = {m.group(1): m.group(2) for m in re.finditer(define_pattern, line)}
    if set(dd.keys()) > feature_definition_keys:
        raise Exception("undefined feature pattern.")

    depend_column_name = format_utils.split_line(dd['depend'])
    dd['depend_column_num'] = sorted([column_dict[n] for n in depend_column_name])

    def _make_extractor(mdl):
        return mdl.__dict__.get(dd['method'])

    extractor_class = _make_extractor(pm) or _make_extractor(custom_module)
    if not extractor_class:
        raise NotImplementedError("un-predefined method. method name=")
    return extractor_class(dd)


def parse_train_data(data_line, feature_extractors, columns, output_format):
    """
    根据预定义的extractor，解析一行训练数据
    :param data_line:
    :param feature_extractors:
    :return:
    """
    split_line = format_utils.split_line(data_line)
    if len(split_line) != columns:
        raise Exception('columns not match, shoud have %d columns, but %d columns of: %s' % (columns, len(split_line), data_line))
    label = feature_extractors[0].extract(split_line)
    features = {ext: ext.extract(split_line) for ext in feature_extractors[1:]}

    output_formater = globals().get('formater_%s' % output_format)
    feature_line = output_formater(label, features)
    return feature_line


def formater_orig(label, features):
    def p(v):
        if isinstance(v, list):
            return u' '.join(['%s' % i for i in v])
        else:
            return '%s' % v

    fstr = u' '.join(map(p, features.values()))
    return u'%s %s' % (label, fstr)


def formater_liblinear(label, features):
    fea_idx = feature_values_to_liblinear_form(features.values())
    fstr = u' '.join([u'%d:%d' % (sk, fea_idx[sk]) for sk in sorted(fea_idx.keys())])
    return u'%s %s' % (label, fstr)


def feature_values_to_liblinear_form(values):
    """
    从formater_liblinear方法中剥离出来，用于线上Ranker部分共用
    把特征值数值转化成liblinear形式的字典输出
    :param values:
    :return:
    """
    fea_idx = collections.defaultdict(int)

    def _append_one_value(v):
        if v in feature_index_dict:
            idx = feature_index_dict[v]
        else:
            idx = len(feature_index_dict) + 1
            feature_index_dict[v] = idx
        fea_idx[idx] += 1

    for value in values:
        if hasattr(value, '__iter__'):
            for v in value:
                _append_one_value(v)
        else:
            _append_one_value(value)

    return fea_idx



if __name__ == '__main__':
    s = set()
    print len(s)
