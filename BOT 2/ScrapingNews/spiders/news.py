# -*- coding: utf-8 -*-
from typing import Container
import scrapy
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException
from ScrapingNews.items import ScrapingnewsItem
from w3lib.html import replace_escape_chars
import datefinder
import re
import configparser

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC




class NewsSpider(scrapy.Spider):
    name = 'news'

    start_urls = ['https://www.cbsnews.com/latest/us/']
    #allowed_domains = ['coloradosun.com']

    no_of_pages = 100

    def start_requests(self):


        cnt = 1
        while cnt <= self.no_of_pages:
            yield Request(self.start_urls[0]+str(cnt),  callback=self.parse_news)
            cnt =cnt+1

    def parse_news(self, response):

        news_url_list = response.xpath(
            '//article[@class="item  item--type-article item--topic-us"]/a[@class="item__anchor"]/@href').extract()

        for url_item in news_url_list:
            yield Request(url=url_item,  callback=self.parse_news_in_details, meta={'url': url_item
                                                                                    })



    def parse_news_in_details(self, response):
        url = response.meta['url']
        try:
            news = response.xpath(
                '//section[@class="content__body"]/p/text()').extract()

            ScrapingnewsItem_data = ScrapingnewsItem()
            ScrapingnewsItem_data['url'] = url
            ScrapingnewsItem_data['news_content'] = news
            yield ScrapingnewsItem_data

        except :
           pass


