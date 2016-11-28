# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import os

ES_PORT = os.getenv('ELASTICSEARCH_PORT', 9200)
MAX_TTL = os.getenv('MAX_TTL', 30)
ES_URL = os.getenv('ELASTICSEARCH_URL', 'localhost')


class DupFilterMiddleware(object):
    def __init__(self):
        self.es = Elasticsearch([{'host': ES_URL, 'port': ES_PORT}])
        print "DupFilterMiddleware Initialize elasticsearch connection"

    def process_request(self, request, spider):
        for i in range(0, MAX_TTL):
            date_string = 'news-index-' + (datetime.now().date() - timedelta(i)).strftime('%-d_%-m_%-Y')
            if self.es.exists(index=date_string, doc_type='news', id=request.url):
                print "Request url existed, ignore it!!!"
                raise IgnoreRequest()
            else:
                print "Request ok!"
                return None
