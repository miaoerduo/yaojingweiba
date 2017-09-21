# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.loader import ItemLoader

from yaojingweiba.items import ImageItem


class CartoonSpider(scrapy.Spider):
    name = 'cartoon'
    allowed_domains = ['www.yaojingweiba.com']
    start_urls = ['http://www.yaojingweiba.com/manhua/']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Host': 'www.yaojingweiba.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'
    }

    def parse(self, response):
        chapter_list = response.css('.zuobw ul li a')
        chapter_name_list = chapter_list.css('::text').extract()
        chapter_url_list = chapter_list.css('::attr(href)').extract()
        chapter_idx = 0
        for chapter in reversed(list(zip(chapter_name_list, chapter_url_list))):
            yield scrapy.Request(
                url=parse.urljoin(response.url, chapter[1]),
                callback=self.parse_chapter,
                method='GET',
                headers=self.headers,
                meta={
                    'name': '{:05d}'.format(chapter_idx) + chapter[0],
                    'page_idx': 0
                }
            )
            chapter_idx += 1

    def parse_chapter(self, response):
        page_idx = response.meta.get('page_idx', 0)
        chapter_name = response.meta.get('name', '')
        item_loader = ItemLoader(item=ImageItem(), response=response)
        item_loader.add_css('image_url', '.over img::attr(src)')
        item_loader.add_value('chapter_name', chapter_name)
        item_loader.add_value('page_idx', page_idx)
        image_item = item_loader.load_item()

        yield image_item

        if page_idx == 0:
            page_list = response.css('.box1_1 div ul li a::attr(href)').extract()
            page_list = page_list[2:-1]
            for page_url in page_list:
                page_idx += 1
                yield scrapy.Request(
                    url=parse.urljoin(response.url, page_url),
                    callback=self.parse_chapter,
                    method='GET',
                    headers=self.headers,
                    meta={
                        'name': chapter_name,
                        'page_idx': page_idx
                    }
                )



