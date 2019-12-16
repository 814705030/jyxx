# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from copy import deepcopy


class JggsSpider(CrawlSpider):
    name = 'jggs'
    allowed_domains = ['jxsggzy.cn']
    start_urls = ['http://www.jxsggzy.cn/web/jyxx/002006/002006004/1.html']

    def parse(self, response):
        item = {}

        href_list = response.css("div.ewb-infolist a::attr(href)").extract()
        # href_list = response.xpath("//div[@class='ewb-infolist']//a/@href").extract()
        for href in href_list:
            item['href'] = "http://www.jxsggzy.cn" + str(href)
            if re.search('\/201.*\/', item['href']):#  \/201912.*\/  十二月
                yield scrapy.Request(
                    item["href"],
                    callback=self.parse_detail,
                    meta={"item": deepcopy(item)}
                )

        if response.css("li.nextlink a::attr(href)").extract()[0]:
            next_link = "http://www.jxsggzy.cn" + str(response.css("li.nextlink a::attr(href)").extract()[0])
            yield scrapy.Request(
                next_link,
                callback=self.parse,
                meta={"item": item}
            )

    def parse_detail(self, response):
        title = ''
        item = response.meta['item']
        h1 = response.xpath("//div[@class='article-info']/h1/text()").extract()
        for h in h1:
            title = title + h

        item['title'] = title
        if re.search('\[.*?().*?\]', title):
            item['level'] = re.search('\[.*?().*?\]', title).group(0)[1:-1]
        else:
            item['level'] = ''
        if re.search('\].*?().*?公司', title):
            item['company'] = re.search('\].*?().*?公司', title).group(0).lstrip(']')
        else:
            item['company'] = ''
        if re.search('编号：(.*?)[\）,\】,\),\]]', title):
            item['number'] = re.search('编号：(.*?)[\）,\】,\),\]]', title).group(0)[3:-1]
        else:
            item['number'] = ''
        yield item