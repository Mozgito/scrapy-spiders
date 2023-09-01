import json
import random
import re
import scrapy
from scrapy import Request
from ..items import ProductsCrawlerItem

async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderLazada(scrapy.Spider):
    name = "spider_lzd"
    urls = [
        "https://www.lazada.com.ph/shop-womens-top-handle-bags/?ajax=true&isFirstRequest=false&ppath=100005920%3A99561",
        "https://www.lazada.com.ph/shop-womens-tote-bags/?ajax=true&isFirstRequest=false&ppath=100005920%3A99561",
        "https://www.lazada.com.ph/shop-womens-cross-body-bags/?ajax=true&isFirstRequest=false&ppath=100005920%3A99561",
        # "https://www.lazada.com.ph/shop-womens-backpacks/?ajax=true&isFirstRequest=false&ppath=100005920%3A99561"
    ]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "SCRAPEOPS_PROXY_ENABLED": True
    }

    def __init__(self, url_number=None, pages=1, *args, **kwargs):
        super(SpiderLazada, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def _get_meta(self) -> dict:
        return {
            "playwright": True,
            "playwright_include_page": True,
            "errback": errback,
            "sops_country": random.choice(["ru", "jp", "in"])
        }

    def start_requests(self):
        for url in self.urls:
            yield Request(
                url + "&page=1",
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self._get_meta()
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        json_body = re.search(r'(\{"templates".*?)</pre></body></html>', response.text).group(1)
        next_page = int(json.loads(json_body)['mainInfo']['page']) + 1
        total_pages = int(json.loads(json_body)['mainInfo']['pageSize'])
        products = json.loads(json_body)['mods']['listItems']

        for product in products:
            item = ProductsCrawlerItem()
            item['prod_id'] = product['itemId']
            item['name'] = product['name']
            item['url'] = 'https:' + product['itemUrl']
            item['price'] = product['price']
            item['currency'] = 'PHP'
            item['image_urls'] = [product['image']]
            for i in range(0, len(product['thumbs'])):
                if product['thumbs'][i]['image'] not in item['image_urls']:
                    item['image_urls'].append(product['thumbs'][i]['image'])
                if i == 3:
                    break
            item['site'] = 'Lazada'
            item['type'] = 'bags'

            yield item

        if next_page <= total_pages and next_page <= self.pages:
            new_url = re.search(r"(https://www\.lazada\.com\.ph.*&page=)", response.url).group(1)
            yield Request(
                new_url + str(next_page),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self._get_meta()
            )
