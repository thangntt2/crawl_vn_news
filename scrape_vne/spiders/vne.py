# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrape_vne.items import ScrapeVneItem
from bs4 import BeautifulSoup
import re


class VneSpider(CrawlSpider):
    name = "vne"
    r = re.compile('\d+/\d+/\d+')
    allowed_domains = ["vnexpress.net"]
    start_urls = (
        'http://www.vnexpress.net/tin-tuc/thoi-su',
        'http://vnexpress.net/tin-tuc/the-gioi',
        'http://kinhdoanh.vnexpress.net/',
        'http://giaitri.vnexpress.net/'
        'http://thethao.vnexpress.net/',
        'http://vnexpress.net/tin-tuc/phap-luat',
        'http://vnexpress.net/tin-tuc/giao-duc',
        'http://suckhoe.vnexpress.net/',
        'http://giadinh.vnexpress.net/',
        'http://dulich.vnexpress.net/',
        'http://vnexpress.net/tin-tuc/khoa-hoc',
        'http://sohoa.vnexpress.net/',
        'http://vnexpress.net/tin-tuc/oto-xe-may/',
        'http://vnexpress.net/tin-tuc/cong-dong',
    )

    rules = (
        Rule(
            LinkExtractor(allow="tin-tuc/"),
            callback="parse_link",
            follow=False),)

    def parse_link(self, response):
        item = ScrapeVneItem()
        try:
            item['title'] = response.xpath(
                '//h1/text()').extract()[0].encode('utf-8').strip()

            item['description'] = response.xpath(
                '//h3/text()').extract()[0].encode('utf-8').strip()

            item['url'] = response.url.encode('utf-8')
            if len(response.xpath(
                '//div[contains(@class,"fck_detail")]//img/@src').extract())> 0:
                item['image'] = response.xpath(
                    '//div[contains(@class,"fck_detail")]//img/@src').extract()[0].encode('utf-8')
            item['source'] = 'vnexpress.net'
            date_string = BeautifulSoup(
                response.xpath('//div[@class="block_timer left txt_666"]')
                .extract()[0], 'lxml').get_text()
            match = self.r.search(date_string)
            if match:
                item['date'] = match.group().encode('utf-8')
        except IndexError:
            print "list index out of range but its okay!!!"
        except Exception as exception:
            print "an exception has arised!!! " + str(exception)
        yield item
