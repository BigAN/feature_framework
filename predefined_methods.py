#!/usr/env/bin python
# coding=utf8
import re
import logging
import arrow
import base64


__author__ = 'zhuliang'

logger = logging.getLogger(__name__)


class FeatureExctractor(object):
    def __init__(self, conf_dict):
        """
        @:param conf_dict: 一行配置，类似于 label_name=click; depend=action; method=click_or_shown;
                或者 feature_name=aid; slot=a; depend=aid; method=direct;
        @:param column_dict：数据项名称 -> 数据项所在列的列数
        """

        if 'feature_name' in conf_dict:
            self.conf_type = 'feature'
            self.feature_name = conf_dict['feature_name']
        elif 'label_name' in conf_dict:
            self.conf_type = 'label'
            self.label_name = conf_dict['label_name']
        else:
            raise Exception('feature or label?')

        self.depend_column = conf_dict['depend_column_num']
        if 'slot' in conf_dict:
            self.slot_name = conf_dict['slot']
        if 'args' in conf_dict:
            self.additional_args = conf_dict['args']
        self.escaper = self._make_escaper()

    def _make_escaper(self):
        if self.conf_type == 'feature':
            def _escape(feature_value):
                # if isinstance(feature_value, unicode):
                # fv = feature_value.encode('utf8')
                # else:
                #     fv = str(feature_value)
                if isinstance(feature_value, basestring):
                    feature_value = re.sub(r'[\s,:;]+', '_', feature_value)
                try:
                    s = u'%s_%s' % (self.feature_name, feature_value)
                    return s
                except UnicodeDecodeError, e:
                    s = u'%s_%s' % (self.feature_name, base64.b64encode(feature_value))
                    return s

            return _escape
        else:
            return lambda x: x

    def check_depend_columns(self, depend_column_name):
        pass

    def extract(self, split_line):
        depended_column_value = [split_line[column_num] for column_num in self.depend_column]
        feature_value = self.process_columns_value(depended_column_value)
        if isinstance(feature_value, list):
            return map(self.escaper, feature_value)
        return self.escaper(feature_value)

    def process_columns_value(self, columns):
        raise NotImplementedError('not implemented.')


class Direct(FeatureExctractor):
    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) > 1:
            raise Exception("direct only depend one column")

    def process_columns_value(self, columns):
        return columns[0]


class String(FeatureExctractor):
    def __init__(self, conf):
        super(String, self).__init__(conf)
        self.fun = None
        if 'fun' in conf:
            self.fun = conf['fun']

    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) > 1:
            raise Exception("direct only depend one column")

    def process_columns_value(self, columns):
        value = str(columns[0])
        if self.fun is not None:
            mtd = getattr(value, self.fun)
            return mtd()
        else:
            return value


def combine_mutil_columns(columns):
    def _make_rst(old_rst, cur_column):
        if len(old_rst) > 0:
            if isinstance(cur_column, list):
                rtn = []
                for one in cur_column:
                    rtn.extend(['%s_%s' % (r, one) for r in old_rst])
                return rtn
            else:
                return ['%s_%s' % (r, cur_column) for r in old_rst]
        else:
            return map(str, cur_column) if isinstance(cur_column, list) else [str(cur_column)]

    rst = []
    for c in columns:
        rst = _make_rst(rst, c)
    return rst


class Combine(FeatureExctractor):
    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) < 2:
            raise Exception("combine depend more than one column")

    def process_columns_value(self, columns):
        return combine_mutil_columns(columns)


class TimeParser(FeatureExctractor):
    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) > 1:
            raise Exception('need only one.')

    def process_columns_value(self, columns):
        _time = arrow.get(columns[0]).datetime
        rst = ['weekend_%d' % (1 if _time.weekday() < 2 else 0), 'hour_%d' % (int(_time.hour) / 6)]
        return rst


if __name__ == '__main__':
    columns = [1, [2, '3'], ['a', u'你好']]
    print combine_mutil_columns(columns)