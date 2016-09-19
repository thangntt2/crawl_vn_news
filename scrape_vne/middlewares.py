# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

class DupFilterMiddleware(object):
    def __init__(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        print "DupFilterMiddleware Initialize elasticsearch connection"

    def process_request(self, request, spider):
        today = datetime.now()
        for i in range(0,6):
            date_string = 'news-index-' + str((datetime.now().date() - timedelta(i)))
            if self.es.exists(index=date_string, doc_type='news', id=request.url):
                print "Request url existed, ignore it!!!"
                raise IgnoreRequest()
            else:
                print "Request ok!"
                return None
