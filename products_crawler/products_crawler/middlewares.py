# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random
import re
from scrapy import signals, Request
from urllib.parse import urlencode, unquote
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
        "Not/A)Brand",
        "Not)A;Brand"
    ]

    def process_request(self, request, spider):
        chrome_v1 = random.randint(55, 104)
        chrome_v3 = random.randint(0, 3200)
        chrome_v4 = random.randint(0, 100)
        chrome_version = '{}.0.{}.{}'.format(chrome_v1, chrome_v3, chrome_v4)
        os = random.choice(list(self.os_types.keys()))
        brand = random.choice(self.brands)
        brand_version = random.choice([8, 99, 24])

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

        if 'temu.com' in request.url:
            request.headers['Accept-Language'] = 'en-US,en;q=0.9'
            request.headers['Cache-Control'] = 'no-cache'
            request.headers['Pragma'] = 'no-cache'
            request.headers['Referer'] = 'https://www.temu.com/'

        if 'lazada.com.ph' in request.url:
            request.headers['Accept-Language'] = 'en-US,en;q=0.9'
            request.headers['Cache-Control'] = 'no-cache'
            request.headers['Pragma'] = 'no-cache'
            request.headers['Referer'] = 'https://www.lazada.com.ph/'


class ScrapeOpsProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = 'https://proxy.scrapeops.io/v1/?'
        self.scrapeops_proxy_active = settings.get('SCRAPEOPS_PROXY_ENABLED', False)
        self.proxy_site_list = [
            'www.lazada.com.ph',
            'www.temu.com',
        ]

    @staticmethod
    def _param_is_true(request, key):
        if request.meta.get(key) or request.meta.get(key, 'false').lower() == 'true':
            return True
        return False

    @staticmethod
    def _replace_response_url(response):
        url_re = re.search(r"https://proxy.*&url=(.*)", response.url)
        if url_re is not None:
            real_url = url_re.group(1)
        else:
            real_url = response.url

        return response.replace(url=unquote(real_url))

    def _get_scrapeops_url(self, request):
        payload = {'api_key': self.scrapeops_api_key, 'url': request.url}
        if self._param_is_true(request, 'sops_render_js'):
            payload['render_js'] = True
        if self._param_is_true(request, 'sops_residential'):
            payload['residential'] = True
        if self._param_is_true(request, 'sops_keep_headers'):
            payload['keep_headers'] = True
        if request.meta.get('sops_country') is not None:
            payload['country'] = request.meta.get('sops_country')
        proxy_url = self.scrapeops_endpoint + urlencode(payload)
        return proxy_url

    def _scrapeops_proxy_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_proxy_active is False:
            return False
        return True

    def process_request(self, request, spider):
        if self._scrapeops_proxy_enabled is False or \
                self.scrapeops_endpoint in request.url or \
                not any(key in request.url for key in self.proxy_site_list):
            return None

        scrapeops_url = self._get_scrapeops_url(request)
        new_request = request.replace(
            cls=Request, url=scrapeops_url, meta=request.meta)
        return new_request

    def process_response(self, request, response, spider):
        new_response = self._replace_response_url(response)
        return new_response
