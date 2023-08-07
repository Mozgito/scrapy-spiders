# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ProductsCrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ProductsCrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class UserAgentMiddleware(object):
    os_types = {
        'Windows': '(Windows NT 10.0; Win64; x64)',
        'Linux': '(X11; Linux x86_64)',
        'macOS': '(Macintosh; Intel Mac OS X 10_14_6)'
    }
    brands = [
        "(Not(A:Brand",
        " Not A;Brand",
        "Not.A/Brand",
        "Not/A)Brand"
    ]

    def process_request(self, request, spider):
        chrome_v1 = random.randint(55, 104)
        chrome_v3 = random.randint(0, 3200)
        chrome_v4 = random.randint(0, 100)
        chrome_version = '{}.0.{}.{}'.format(chrome_v1, chrome_v3, chrome_v4)
        os = random.choice(list(self.os_types.keys()))
        brand = random.choice(self.brands)
        brand_version = random.choice([8, 99])

        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8;*;q=0.5'
        request.headers['Cache-Control'] = 'max-age=0'
        request.headers['Sec-Ch-Ua'] = '"{}";v="{}", "Chromium";v="{}", "Google Chrome";v="{}"' \
            .format(brand, brand_version, chrome_v1, chrome_v1)
        request.headers['Sec-CH-Ua-Full-Version'] = chrome_version
        request.headers['Sec-Ch-Ua-Full-Version-List'] = '"{}";v="{}.0.0.0", "Chromium";v="{}", "Google Chrome";v="{}"'\
            .format(brand, brand_version, chrome_version, chrome_version)
        request.headers['Sec-Ch-Ua-Mobile'] = '?0'
        request.headers['Sec-Ch-Ua-Platform'] = os
        request.headers['Sec-Fetch-Dest'] = 'document'
        request.headers['Sec-Fetch-Mode'] = 'navigate'
        request.headers['Sec-Fetch-Site'] = 'same-origin'
        request.headers['Sec-Fetch-User'] = '?1'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        request.headers['User-Agent'] = ' '.join([
            'Mozilla/5.0',
            self.os_types[os],
            'AppleWebKit/537.36',
            '(KHTML, like Gecko)',
            'Chrome/' + chrome_version,
            'Safari/537.36'
        ])

        if 'amazon.com' in request.url:
            request.headers['Accept-Language'] = 'en-US,en;q=0.9'
            request.headers['Cache-Control'] = 'no-cache'
            request.headers['Pragma'] = 'no-cache'
            request.headers['Referer'] = 'https://www.google.com/'
            request.headers['Sec-Fetch-Dest'] = 'empty'
            request.headers['Sec-Fetch-Mode'] = 'cors'

        if 'shopee.ph' in request.url:
            request.headers['Accept-Language'] = 'en-US,en;q=0.9'
            request.headers['Referer'] = 'https://shopee.ph/'
            request.headers['X-Api-Source'] = 'pc'
            request.headers['X-Requested-With'] = 'XMLHttpRequest'
            request.headers['X-Shopee-Language'] = 'en'
