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


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderTemu(scrapy.Spider):
    name = "spider_temu"
    urls = [
        "https://www.temu.com/ph-en/womens-tote-bags-o3-736.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/ph-en/womens-handbags-o3-735.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/ph-en/womens-shoulder-bags-o3-738.html?filter_items=P121:26569|0:1",
        "https://www.temu.com/ph-en/womens-crossbody-bags-o3-740.html?filter_items=P121:26569|0:1",
    ]
    price_filters = [
        "|104:170,399",
        "|104:400,599",
        "|104:600,699",
        "|104:700,899",
        "|104:900,1199",
        "|104:1200,1999",
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "SCRAPEOPS_PROXY_ENABLED": True
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "errback": errback,
        "sops_country": random.choice(["us", "de", "es", "fr", "uk", "it", "ca", "br", "in"])
    }

    def __init__(self, url_number=None, *args, **kwargs):
        super(SpiderTemu, self).__init__(*args, **kwargs)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            for price_filter in self.price_filters:
                yield Request(
                    url + price_filter,
                    callback=self.parse,
                    method="GET",
                    dont_filter=True,
                    meta=self.meta
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
            item['currency'] = 'PHP'
            item['image_urls'] = [product['data']['image']['url']]
            item['site'] = 'Temu'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            yield item
