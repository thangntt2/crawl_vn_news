# -*- coding: utf-8 -*-
from scrapy.exceptions import IgnoreRequest
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import os

ES_PORT = os.getenv('ES_PORT', 8889)
MAX_TTL = os.getenv('MAX_TTL', 30)
ES_PORT = os.getenv('ELASTICSEARCH_PORT', 443)
ES_URL = os.getenv('ELASTICSEARCH_URL', 'https://wji4cg72wu:1lr4slrzuz@acme-development-8779249584.us-east-1.bonsai.io/')

class DupFilterMiddleware(object):
    def __init__(self):
        self.es = Elasticsearch([{'host': ES_URL, 'port': ES_PORT}])
        print "DupFilterMiddleware Initialize elasticsearch connection"

    def process_request(self, request, spider):
        today = datetime.now()
        for i in range(0, MAX_TTL):
            date_string = 'news-index-' + str((datetime.now().date() - timedelta(i)))
            if self.es.exists(index=date_string, doc_type='news', id=request.url):
                print "Request url existed, ignore it!!!"
                raise IgnoreRequest()
            else:
                print "Request ok!"
                return None
