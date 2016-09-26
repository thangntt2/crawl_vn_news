# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrape_vne.items import ScrapeVneItem
from bs4 import BeautifulSoup
import re


class VnMediaSpider(CrawlSpider):
    name = "vnmedia"
    r = re.compile('\d+/\d+/\d+')
    allowed_domains = ["vnmedia.vn"]
    start_urls = [
        "http://vnmedia.vn/quoc-te",
        "http://vnmedia.vn/dan-sinh",
        "http://vnmedia.vn/the-gioi-phang",
        "http://vnmedia.vn/van-hoa",
        "http://vnmedia.vn/thi-truong",
        "http://vnmedia.vn/oto-xe-may",
        "http://vnmedia.vn/the-thao",
        "http://vnmedia.vn/du-lich",
        "http://vnmedia.vn/the-gioi-phang/VNPT-ket-noi"
    ]

    rules = (
        Rule(
            LinkExtractor(),
            callback="parse_link",
            follow=False),)

    def parse_link(self, response):
        item = ScrapeVneItem()
        try:
            item['title'] = response.xpath(
                '//h1/text()').extract()[0].encode('utf-8').strip()

            item['description'] = response.xpath('//p[@style="text-align: justify;"]/strong/text()').extract()[0].encode('utf-8').strip()

            if len(item['description']) == 0:
                item['description'] = response.xpath(
                    '//div[@class="short_intro txt_666"]/text()').extract()[0].encode('utf-8').strip()

            item['url'] = response.url.encode('utf-8')
            if len(response.xpath(
                '//td/img/@src').extract())> 0:
                item['image'] = "http://vnmedia.vn/"+response.xpath(
                    '//td/img/@src').extract()[0].encode('utf-8')
            item['source'] = 'vnmedia.vn'

            date_string = response.xpath('//div[@class="date"]/text()').extract()[0]
            match = self.r.search(date_string)
            if match:
                item['date'] = match.group().encode('utf-8')
        except IndexError:
            print "list index out of range but its okay!!!"
        except Exception as exception:
            print "an unexpected exception has arised!!! " + str(exception)
        yield item
