import json
import re
import scrapy
import time
from scrapy import Request
from ..items import ProductItem


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderShopee(scrapy.Spider):
    name = "spider_shopee"
    urls = [
        "https://shopee.ph/api/v4/recommend/recommend?bundle=category_landing_page&cat_level=2&catid=11021942",  # Shoulder bags
        "https://shopee.ph/api/v4/recommend/recommend?bundle=category_landing_page&cat_level=2&catid=11021948",  # Tote bags
        "https://shopee.ph/api/v4/recommend/recommend?bundle=category_landing_page&cat_level=2&catid=11021936",  # Handbags
        "https://shopee.ph/api/v4/recommend/recommend?bundle=category_landing_page&cat_level=2&catid=11021954"  # Backpacks
    ]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "errback": errback
    }

    non_url_safe = [
        '"', '#', '$', '%', '&', '+',
        ',', '/', ':', ';', '=', '?',
        '@', '[', '\\', ']', '^', '`',
        '{', '|', '}', '~', ' '
    ]
    non_url_safe_regex = re.compile(
        r'[{}]'.format(''.join(re.escape(x) for x in non_url_safe)))

    def __init__(self, url_number=None, *args, **kwargs):
        super(SpiderShopee, self).__init__(*args, **kwargs)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            yield Request(
                url + "&limit=100&offset=0",
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        json_body = re.search(r'(\{"bff_meta".*?)</pre></body></html>', response.text).group(1)
        has_more_items = json.loads(json_body)['data']['sections'][0]['has_more']
        products = json.loads(json_body)['data']['sections'][0]['data']['item']

        for product in products:
            item = ProductItem()
            item['prod_id'] = product['itemid']
            item['name'] = product['name']
            item['url'] = self.slugify_product_url(product)
            item['price'] = product['price'] / 100000
            item['currency'] = 'PHP'
            item['image_urls'] = ['https://down-ph.img.susercontent.com/file/' + product['image']]
            for i in range(1, len(product['images'])):
                item['image_urls'].append('https://down-ph.img.susercontent.com/file/' + product['images'][i])
                if i == 2:
                    break
            item['site'] = 'Shopee'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            yield item

        if has_more_items:
            new_url = re.search(r'(https.*?offset=)', response.url).group(1)
            new_offset = int(re.search(r'(https.*?offset=)(\d*)', response.url).group(2)) + 100
            yield Request(
                new_url + str(new_offset),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )

    def slugify_product_url(self, product):
        name = self.non_url_safe_regex.sub('-', product['name'] + '-')
        name = re.sub(r'--+', '-', name)

        return "https://shopee.ph/{}i.{}.{}".format(name, product['shopid'], product['itemid'])
