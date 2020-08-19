# -*- coding: utf-8 -*-
import scrapy
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException
from TechnologyNewsScraping.items import TechnologynewsscrapingItem
from w3lib.html import replace_escape_chars
import datefinder
import re


class TechnologySpider(scrapy.Spider):
    name = 'Technology'
    allowed_domains = ['aninews.in',
                       'hindustantimes.com',
                       'livemint.com',
                       'independent.co.uk',
                       'theguardian.com',
                       'theprint.in',
                       'dailymail.co.uk',
                       'engadget.com',
                       'techcrunch.com',
                       'in.reuters.com',
                       'inc42.com',
                       'engadget.com',
                       'digit.in',
                       'reuters.com',
                       'thenextweb.com',
                       'yourstory.com',
                       'entrackr.com',
                       'deccanherald.com',
                       'imesnownews.com',
                       'thenextweb.com']
    start_urls = ['http://www.inshorts.com/en/read/technology']

    doc_id = -1
    no_of_pages = 80

    def start_requests(self):
        url = 'http://www.inshorts.com/en/read/technology'
        # self.driver = webdriver.Chrome(
        #     'C:/Users/sujit koley/OneDrive - IIT Hyderabad/NLP Assignment/Assignment 1/chromedriver')

        self.driver = webdriver.Chrome('chromedriver')
        self.driver.get(self.start_urls[0])
        cnt = 1
        while cnt <= self.no_of_pages:
            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="load-more-wrapper"]/div[text()="Load More"]')
                sleep(10)
                self.logger.info('Sleeping for 10 seconds.')
                next_page.click()

                cnt += 1
            except NoSuchElementException:
                self.logger.info('No more pages to load.')

                break
        source_page = self.driver.page_source
        self.driver.quit()
        yield Request(url,  callback=self.parse_short_news, meta={'source_page': source_page
                                                                  })

    def parse_short_news(self, response):
        source_page = response.meta['source_page']
        sel = Selector(text=source_page)
        block_of_news_list = sel.xpath(
            '//div[@class="news-card z-depth-1"]').extract()

        more_details_url_list = []
        title_list = []

        # fetch news only if it has url details
        for block_of_news in block_of_news_list:
            block_of_news_sel = Selector(text=block_of_news)

            more_details_url = block_of_news_sel.xpath(
                '//div[@class="read-more"]/a/@href').extract_first()

            if more_details_url:
                title = block_of_news_sel.xpath(
                    '//div[@class="news-card-title news-right-box"]/a/span/text()').extract_first()
                more_details_url_list.append(more_details_url)
                title_list.append(title)

        for title, more_details_url in zip(title_list, more_details_url_list):
            yield Request(more_details_url,  callback=self.parse_short_news_in_details, meta={'title': title,
                                                                                              'url': more_details_url
                                                                                              })

    def parse_short_news_in_details(self, response):

        title = response.meta['title']
        url = response.meta['url']
        meta_keyword = response.xpath(
            "//meta[@name='keywords']/@content").extract_first()

        content_item_list = response.xpath(
            "//body//p//text()").extract()

        # content_item_list = [content_item for content_item in content_item_list if len(
        #     content_item.split(" ")) > 8 and not (len(list(datefinder.find_dates(content_item)))>0 and 'published' in content_item.lower())]

        content_item_list = [content_item for content_item in content_item_list if
                             not (len(list(datefinder.find_dates(content_item)))
                                  > 0 and 'published' in content_item.lower())
                             ]
        # remove hyperlink
        content_item_list = [
            re.sub('https://.*', "", content_item) for content_item in content_item_list]

        content = " ".join(content_item_list).encode(
            'ascii', 'ignore').decode("utf-8").strip()

        self.doc_id = self.doc_id+1
        file_name = "data/content_file/content_"+str(self.doc_id)+".txt"
        with open(file_name, "w") as f:
            f.write(content)

        TechnologynewsscrapingItem_data = TechnologynewsscrapingItem()
        TechnologynewsscrapingItem_data['title'] = title
        TechnologynewsscrapingItem_data['url'] = url
        TechnologynewsscrapingItem_data['doc_id'] = self.doc_id
        TechnologynewsscrapingItem_data['meta_keyword'] = meta_keyword
        TechnologynewsscrapingItem_data['content'] = file_name

        yield TechnologynewsscrapingItem_data
