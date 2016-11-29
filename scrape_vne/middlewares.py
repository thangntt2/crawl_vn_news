# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
import pymysql.cursors
import os

MAX_TTL = os.getenv('MAX_TTL', 30)


class DupFilterMiddleware(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PW'),
            db=os.getenv('MYSQL_DB'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursors = self.connection.cursor()
        create_table_sql = 'CREATE TABLE IF NOT EXISTS `parsed_url` (' \
            + '`id` int(11) unsigned NOT NULL AUTO_INCREMENT,' \
            + '`url` text NOT NULL,' \
            + '`createdAt` datetime NOT NULL,' \
            + 'PRIMARY KEY (`id`)' \
            + ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'
        self.cursors.execute(create_table_sql)
        print "DupFilterMiddleware Initialize mysql connection"
        self.check_sql = 'SELECT * FROM `parsed_url` WHERE url=%s'
        self.insert_sql = 'INSERT INTO `parsed_url` (`url`, `createdAt`)' \
            + ' VALUES (%s, NOW())'

    def spider_closed(self, spider, reason):
        self.connection.close()

    def process_request(self, request, spider):
        if self.cursors.execute(self.check_sql, (request.url)) > 0:
            print "Request url existed, ignore it!!!"
            raise IgnoreRequest()
        else:
            print "Request ok!"
            self.cursors.execute(self.insert_sql, (request.url))
            self.connection.commit()
            return None
