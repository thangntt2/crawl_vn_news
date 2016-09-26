# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrape_vne.items import ScrapeVneItem
from bs4 import BeautifulSoup
import re
from datetime import datetime

class Xahoithongtin(CrawlSpider):
    name = "xahoithongtin"
    r = re.compile('\d+/\d+/\d+')
    allowed_domains = ["xahoithongtin.com.vn"]
    start_urls = (
        'http://xahoithongtin.com.vn/thi-truong',
        'http://xahoithongtin.com.vn/vien-thong-cntt/',
        'http://xahoithongtin.com.vn/san-pham-so',
        'http://xahoithongtin.com.vn/trai-nghiem',
        'http://xahoithongtin.com.vn/o-to-xe-may',
        'http://xahoithongtin.com.vn/Do-choi-so',
        'http://xahoithongtin.com.vn/choi-va-thu-gian',
        'http://xahoithongtin.com.vn/cong-nghe-quan-su'
    )

    rules = (
        Rule (LinkExtractor(), callback="parse_link", follow=False),
        )

    def parse_link(self, response):
        item = ScrapeVneItem()
        try:
            item['title'] = response.xpath('//h1/text()')[0].extract().encode('utf-8').strip()
            item['description'] = response.xpath('//div[@class="clearfix"]//strong/span/span/text()').extract()[0].encode('utf-8').strip()
            item['url'] = response.url.encode('utf-8')
            if len(response.xpath(
                '//td/img/@src').extract())> 0:
                item['image'] = "http://xahoithongtin.com.vn/"+response.xpath(
                    '//td/img/@src').extract()[0].encode('utf-8')
            item['source'] = 'xahoithongtin.com.vn'
            date_string = response.xpath('//div[@class="date"]/text()').extract()[0]
            match = self.r.search(date_string)
            if match:
                item['date'] = match.group().encode('utf-8')
        except IndexError as indexException:
            print "list index out of range but its okay!!!"
        except Exception as exception:
            print "an exception has arised!!! " + str(exception)
        yield item
