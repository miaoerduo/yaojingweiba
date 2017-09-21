# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import shutil

import requests
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

from yaojingweiba.settings import IMAGE_FINAL_STORE, IMAGES_STORE



class MyImagesPipeline(ImagesPipeline):
    def handle_redirect(self, url):
        response = requests.head(url)
        if response.status_code == 302:
            url = response.headers['Location']
        return url

    def get_media_requests(self, item, info):
        if 'image_url' not in item:
            raise DropItem("Item contains no files")
        for url in item['image_url']:
            if not url:
                continue
            url = self.handle_redirect(url)
            yield scrapy.Request(url)

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")

        chapter_dir = os.path.join(IMAGE_FINAL_STORE, item['chapter_name'][0])
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        for file_name in file_paths:
            suffix = file_name.split('.')[-1]
            shutil.move(os.path.join(IMAGES_STORE, file_name),
                        os.path.join(chapter_dir, '{:05d}.{}'.format(item['page_idx'][0], suffix)))
        return item