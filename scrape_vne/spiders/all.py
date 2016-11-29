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
from scrapy.exceptions import CloseSpider

GET_LIST_NEWS_SQL = 'SELECT * FROM `News` WHERE name = %s'


def getFirstLine(paragraph):
    lines = paragraph.split('\n')
    for line in lines:
        if len(line.strip()) > 50:
            return line.strip()


class AllSpider(Spider):
    name = "all"
    allowed_domains = []
    start_urls = []

    def __init__(self, newsprovider='', *args, **kwargs):
        super(AllSpider, self).__init__(*args, **kwargs)
        self.newsprovider = newsprovider

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
            print self.newsprovider
            n = cursor.execute(GET_LIST_NEWS_SQL, self.newsprovider)
            if n == 0:
                raise CloseSpider('news provider not available!')
            news = cursor.fetchone()

            self.allowed_domains.append(news['baseurl'])
            newspp = newspaper.build(news['baseurl'])
            for cate in newspp.category_urls():
                if cate not in self.start_urls:
                    self.start_urls.append(cate)
                    request = scrapy.Request(
                        cate,
                        callback=self.parse_link
                    )
                    yield request
        finally:
            print 'connection closed'
            connection.close()

    def parse_link(self, response):
        for link in LinkExtractor().extract_links(response):
            request = scrapy.Request(link.url, callback=self.parse_article)
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
        item['source'] = self.newsprovider

        yield item
