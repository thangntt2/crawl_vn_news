# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json
import os

MAX_TTL = os.getenv('MAX_TTL', 30)
ES_PORT = os.getenv('ES_PORT', 9200)
ES_HOST = os.getenv('ES_HOST', 'localhost')


class ScrapeVnePipeline(object):
    es_body = {
        "settings": {
            "index": {
                "analysis": {
                    "analyzer": {
                        "suggests_analyzer": {
                            "tokenizer": "lowercase",
                            "filter": [
                                "lowercase",
                                "shingle_filter"
                            ],
                            "type": "custom"
                        }
                    },
                    "filter": {
                        "shingle_filter": {
                            "min_shingle_size": 2,
                            "max_shingle_size": 3,
                            "type": "shingle"
                        }
                    }
                },
                "number_of_shards": "5",
                "number_of_replicas": "1",
            }
        },
        "mappings": {
            "news": {
                "properties": {
                    "_values": {
                        "properties": {
                            "date": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "description": {
                                "analyzer": "suggests_analyzer",
                                "type": "string",
                            },
                            "image": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "title": {
                                "analyzer": "suggests_analyzer",
                                "type": "string",
                            },
                            "url": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    }
                }
            }
        }
    }

    def __init__(self):
        self.es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
        print 'ScrapyeVnePipeline Initialize elasticsearch connection'

    def process_item(self, item, spider):
        item_date = datetime.strptime(item['date'], '%d/%m/%Y')
        if (datetime.now().date() - item_date.date()).days < MAX_TTL:
            status = self.es.indices.create(index='news_index-' + item['date'].replace("/", "_"), body=self.es_body, ignore=400)
            if 'acknowledged' in status and status['acknowledged']:
                self.es.indices.delete(index='news_index-' + (item_date - timedelta(MAX_TTL)).date().strftime('%-d_%-m_%-Y'), ignore=404)
            self.es.index(index='news_index-' + item['date'].replace("/", "_"), doc_type='news', id=item['url'], body=json.dumps(dict(item)), ignore=400)
        return item
