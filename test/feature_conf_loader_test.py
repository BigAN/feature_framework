#!/usr/env/bin python
# coding=utf8
import unittest
import os

from data_serv.feature_framework.format_utils import split_line
import data_serv.feature_framework.predefined_methods as pm
import data_serv.feature_framework.feature_conf_loader as feature_conf_loader


class FeatureLoaderTest(unittest.TestCase):
    def test_split_line(self):
        s = r'a, b ,d'
        self.assertItemsEqual(split_line(s), ['a', 'b', 'd'])
        s = r'a, b ,d      \,e'
        self.assertItemsEqual(split_line(s), ['a', 'b', 'd      ,e'])
        s = r'a, b ,,d'
        self.assertRaises(Exception, split_line, s)
        print 'test split line OK.'


    # def test_predefined_method(self):
    #     splited_line = ['abc', 'xyz', '1 23', u'你好']
    #
    #     p_direct = pm.direct_partial([3])
    #     self.assertEqual(p_direct(splited_line), splited_line[3])
    #     with self.assertRaises(Exception):
    #         pm.direct_partial([2, 3])
    #
    #     self.assertEqual(pm.combine_partial([0, 1])(splited_line), 'abc_xyz')
    #     with self.assertRaises(Exception):
    #         pm.combine_partial([0])
    #     print 'test predefined method OK'

    def test_feature_format(self):
        _cur_dir = os.path.dirname(os.path.abspath(__file__))
        feature_conf_file = os.path.join(_cur_dir, 'feature_conf_test.txt')
        feature_data = os.path.join(_cur_dir, 'input_data.txt')
        output_file_path = os.path.join(_cur_dir, 'test_output.txt')
        feature_conf_loader.process(feature_conf_file, feature_data, output_file_path, 'orig')
        print 'test feature format OK'


if __name__ == '__main__':
   unittest.main()


