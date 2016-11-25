# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
import scrapy
from scrapy.linkextractors import LinkExtractor
from newspaper import Article
import newspaper
import pymysql.cursors
import os
from datetime import datetime
from scrape_vne.items import ScrapeVneItem

GET_LIST_NEWS_SQL = 'SELECT * FROM `News`'


def getFirstLine(paragraph):
    lines = paragraph.split('\n')
    for line in lines:
        if len(line.strip()) > 50:
            return line.strip()


class AllSpider(Spider):
    name = "all"
    allowed_domains = []
    start_urls = []

    def start_requests(self):
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PW'),
            db=os.getenv('MYSQL_DB'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            cursor = connection.cursor()
            cursor.execute(GET_LIST_NEWS_SQL)
            results = cursor.fetchall()
            for news in results:
                self.allowed_domains.append(news['baseurl'])
                newspp = newspaper.build(news['baseurl'])
                for cate in newspp.category_urls():
                    if cate not in self.start_urls:
                        self.start_urls.append(cate)
                        request = scrapy.FormRequest(cate, callback=self.parse_link)
                        request.meta['source'] = news['name']
                        yield request
        finally:
            connection.close()

    def parse_link(self, response):
        for link in LinkExtractor(allow=response.meta['source'],).extract_links(response):
            request = scrapy.FormRequest(link.url, callback=self.parse_article)
            request.meta['source'] = response.meta['source']
            yield request

    def parse_article(self, response):
        item = ScrapeVneItem()
        item['url'] = response.url

        article = Article(response.url)
        article.download()
        article.parse()
        images = article.top_image
        if len(images) > 0:
            item['image'] = images
        try:
            item['date'] = article.publish_date.date().strftime('%d/%m/%Y')
        except AttributeError:
            item['date'] = datetime.now().date().strftime('%d/%m/%Y')
        item['title'] = article.title
        item['url'] = article.url
        item['description'] = getFirstLine(article.text)
        item['source'] = response.meta['source']

        yield item
