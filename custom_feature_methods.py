#!/usr/env/bin python
# coding=utf8

__author__ = 'zhuliang'

from bson.objectid import ObjectId
import pymongo

from data_serv.feature_framework.predefined_methods import FeatureExctractor


class ClickOrShown(FeatureExctractor):
    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) > 1:
            raise Exception("only need one column for click or shown label. columns=(%s)", ','.join(depend_column_name))

    def process_columns_value(self, columns):
        if columns[0] == 'click':
            return "+1"
        elif columns[0] == 'shown':
            return "-1"
        else:
            raise Exception('unkonw value!')


class ArticleFeature(FeatureExctractor):
    def __init__(self, conf_dict):
        super(ArticleFeature, self).__init__(conf_dict)
        self.coll = pymongo.MongoClient('mongodb://101.251.192.178:27017/test')['test']['document']

    def check_depend_columns(self, depend_column_name):
        if len(depend_column_name) > 1:
            raise Exception("only need one column for article feature. columns=(%s)", ','.join(depend_column_name))

    def process_columns_value(self, columns):
        article_id = columns[0]
        article = self.coll.find_one({"_id": ObjectId(article_id)})
        rst = []
        rst.append('notorig' if 'rawID' not in article else 'orig')
        rst.append('like_%d' % (article.get('likeNum', 0) / 100))
        rst.append('read_%d' % min(100, (article.get('readNum', 0) / 1000)))
        if 'attrs' in article:
            rst.append(u'sn_%s' % article['attrs']['sourceName'])
            rst.append(u'st_%s' % article['attrs']['sourceType'])
        return rst

if __name__ == '__main__':
    coll = pymongo.MongoClient('mongodb://101.251.192.178:27017/test')['test']['document']
    article = coll.find_one({"_id": ObjectId('55126c6a6bdcdc12738b456a')})
    title = article['title'].encode('utf8')
    print type(title), title





