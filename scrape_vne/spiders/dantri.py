# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrape_vne.items import ScrapeVneItem
from bs4 import BeautifulSoup
import re
from datetime import datetime

class DantriSpider(CrawlSpider):
    name = "dantri"
    r = re.compile('\d+/\d+/\d+')
    allowed_domains = ["dantri.com.vn"]
    start_urls = (
        'http://www.dantri.com.vn/su-kien.htm',
        'http://www.dantri.com.vn/xa-hoi.htm',
        'http://www.dantri.com.vn/the-gioi.htm',
        'http://www.dantri.com.vn/the-thao.htm'
        'http://www.dantri.com.vn/giao-duc-khuyen-hoc.htm',
        'http://www.dantri.com.vn/tam-long-nhan-ai.htm',
        'http://www.dantri.com.vn/kinh-doanh.htm',
        'http://www.dantri.com.vn/van-hoa.htm',
        'http://www.dantri.com.vn/giai-tri.htm',
        'http://dulich.dantri.com.vn/',
        'http://dantri.com.vn/phap-luat.htm',
        'http://dantri.com.vn/nhip-song-tre.htm',
        'http://dantri.com.vn/suc-khoe.htm',
        'http://dantri.com.vn/suc-manh-so.htm',
        'http://dantri.com.vn/o-to-xe-may.htm',
        'http://dantri.com.vn/tinh-yeu-gioi-tinh.htm',
        'http://dantri.com.vn/chuyen-la.htm',
    )

    rules = (
    	Rule (LinkExtractor(), callback="parse_link", follow=False),
		)

    def parse_link(self, response):
		item = ScrapeVneItem()
		try:
			item['title'] = response.xpath('//h1/text()')[0].extract().encode('utf-8').strip()
			if len(response.xpath('//h2/text()').extract()) > 0:
				item['description'] = response.xpath('//h2/text()').extract()[0].encode('utf-8').strip()
			else:
				item['description'] = response.xpath('//h3/text()').extract()[0].encode('utf-8').strip()			
			item['url'] = response.url.encode('utf-8')
			if len(response.xpath('//img[@type="photo"]/@src').extract()) > 0:
				item['image'] = response.xpath('//img[@type="photo"]/@src').extract()[0].encode('utf-8')
			item['source'] = 'dantri.com.vn'
			date_string = BeautifulSoup(response.xpath('//span[@class="fr fon7 mr2 tt-capitalize"]/text()').extract()[0], 'lxml').get_text()
			match = self.r.search(date_string)
			if match:
				item['date'] = match.group().encode('utf-8')
		except IndexError as indexException:
			print "list index out of range but its okay!!!"
		except Exception as exception:
			print "an exception has arised!!! " + str(exception)
		yield item
