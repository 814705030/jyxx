# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from copy import deepcopy


class CgggSpider(CrawlSpider):
    name = 'cggg'
    allowed_domains = ['jxsggzy.cn']
    start_urls = ['http://www.jxsggzy.cn/web/jyxx/002006/002006001/1.html']

    def parse(self, response):
        item = {}

        href_list = response.css("div.ewb-infolist a::attr(href)").extract()
        # href_list = response.xpath("//div[@class='ewb-infolist']//a/@href").extract()
        for href in href_list:
            item['href'] = "http://www.jxsggzy.cn" + str(href)

            if re.search('\/201.*\/', item['href']):  # re.search('\/201912.*\/', item['href'])十二月
                yield scrapy.Request(
                    item["href"],
                    callback=self.parse_detail,
                    meta={"item": deepcopy(item)}  # 多线程写入item，深拷贝以防重复
                )

        if response.css("li.nextlink a::attr(href)").extract()[0]:
            next_link = "http://www.jxsggzy.cn" + str(response.css("li.nextlink a::attr(href)").extract()[0])
            print(next_link)
            yield scrapy.Request(
                next_link,
                callback=self.parse,
                meta={"item": item}
            )

    def parse_detail(self, response):
        title = ''
        item = response.meta['item']
        h1 = response.xpath("//div[@class='article-info']/h1/text()").extract()
        title = "".join(h1)  # 标题被分开了成列表了，循环合起来

        item['title'] = title
        # print(title)
        if re.search('\[.*?().*?\]', title):
            item['level'] = re.search('\[.*?().*?\]', title).group(0)[1:-1]  # 归属地
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
        # context_list = response.xpath("//div[@class='con']//span/text()").extract()
        # if ('联系人：') in context_list:
        #     print(context_list.index('联系人：'))
        # # context = "".join(context_list)
        # # context_no_space = "".join(context.split())
        # print(item['href'], )
        # print('-' * 30)
        yield item
