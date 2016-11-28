# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import os

ES_PORT = os.getenv('ES_PORT', 9200)
ES_HOST = os.getenv('ES_HOST', 'localhost')
MAX_TTL = os.getenv('MAX_TTL', 30)


class DupFilterMiddleware(object):
    def __init__(self):
        self.es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
        print "DupFilterMiddleware Initialize elasticsearch connection"

    def process_request(self, request, spider):
        for i in range(0, MAX_TTL):
            date_string = 'news_index-' + (datetime.now().date() - timedelta(i)).strftime('%d_%m_%Y')
            if self.es.exists(index=date_string, doc_type='news', id=request.url):
                print "Request url existed, ignore it!!!"
                raise IgnoreRequest()
            else:
                print "Request ok!"
                return None
