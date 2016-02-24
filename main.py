#!/usr/env/bin python
# coding=utf8

__author__ = 'zhuliang'

import os
import argparse


def init_argument():
    def exsit_file_path(p):
        if os.path.exists(p) and os.path.isfile(p):
            return p
        else:
            raise argparse.ArgumentTypeError('%s not a existing file.' % p)

    def not_exist_file(p):
        if os.path.exists(p):
            raise argparse.ArgumentTypeError('%s already exist!' % p)
        else:
            return p

    def output_format(m):
        formats = set(['orig', 'liblinear', 'vw'])
        if m in formats:
            return m
        raise argparse.ArgumentTypeError('format %s not supported!' % m)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, type=exsit_file_path, dest='feature_conf',
                        help='absolute path for feature configure file.')
    parser.add_argument('-d', required=True, type=exsit_file_path, dest='data',
                        help='absolute path for input feature data file.')
    parser.add_argument('-o', required=True, type=not_exist_file, dest='output_file',
                        help='absolute path for output file.')
    parser.add_argument('-m', required=True, type=output_format, dest='output_format',
                        help="output format('orig', 'liblinear', 'vw')")
    parser.add_argument('-e', required=False, dest='feature_index',
                        help="file for save feature index map in json")
    return parser.parse_args()


if __name__ == '__main__':
    args = init_argument()
    if args.output_format == 'liblinear' and not args.feature_index:
        raise argparse.ArgumentTypeError('output in liblinear format need feature_data be specified')

    import data_serv.feature_framework.feature_conf_loader as fc_loader
    fc_loader.process(args.feature_conf, args.data, args.output_file, args.output_format, args.feature_index)
