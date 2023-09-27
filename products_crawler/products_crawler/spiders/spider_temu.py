import re
import json
import random
import scrapy
import time
from scrapy import Request
from ..items import ProductItem

BLOCK_RESOURCE_TYPES = [
    "beacon",
    "image",
    "media",
    "ping",
    "websocket",
    "xhr",
    "script"
]

BLOCK_RESOURCE_NAMES = [
    "facebook",
    "google",
    "googletagmanager"
]


def abort_request(request):
    if "api/poppy/v1/opt" not in request.url and \
            (request.method.lower() == "post" or
             any(key in request.resource_type for key in BLOCK_RESOURCE_TYPES) or
             any(key in request.url for key in BLOCK_RESOURCE_NAMES)):
        return True

    return False


class SpiderTemu(scrapy.Spider):
    name = "spider_temu"
    urls = [
        "https://www.temu.com/womens-tote-bags-o3-736.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/womens-shoulder-bags-o3-738.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/womens-crossbody-bags-o3-740.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/womens-handbags-o3-735.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/womens-backpacks-o3-742.html?filter_items=P121:26569|0:1",
    ]
    price_filters = [
        "|104:3.5,8.99",
        "|104:9,11.99",
        "|104:12,15.99",
        "|104:16,19.99",
        "|104:20,23.99",
        "|104:24,28.99",
        "|104:29,39.99",
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "SCRAPEOPS_PROXY_ENABLED": True
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "sops_country": "us"
    }

    def __init__(self, url_number=None, *args, **kwargs):
        super(SpiderTemu, self).__init__(*args, **kwargs)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            if re.search(r'backpacks', url) is not None:
                yield Request(
                    url,
                    callback=self.parse,
                    method="GET",
                    dont_filter=True,
                    meta=self.meta,
                    errback=self.errback
                )
            else:
                for price_filter in self.price_filters:
                    yield Request(
                        url + price_filter,
                        callback=self.parse,
                        method="GET",
                        dont_filter=True,
                        meta=self.meta,
                        errback=self.errback
                    )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        json_body = re.search(r'window\.rawData=(\{"store".*?);document\.dispatchEvent', response.text).group(1)
        products = json.loads(json_body)['store']['goodsList']

        for product in products:
            item = ProductItem()
            item['prod_id'] = product['data']['goodsId']
            item['name'] = product['data']['title']
            item['url'] = 'https://www.temu.com' + re.search(r"(.*?\.html)\?", product['data']['seoLinkUrl']).group(1)
            item['price'] = product['data']['priceInfo']['priceSchema']
            item['currency'] = product['data']['priceInfo']['currency']
            item['image_urls'] = [product['data']['image']['url']]
            item['site'] = 'Temu'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            if item['currency'] != 'USD':
                self.log("Temu. Wrong currency: {}. URL: {}".format(item['currency'], response.url), 40)
                break

            yield item

    async def errback(self, response):
        page = response.request.meta["playwright_page"]
        await page.close()
