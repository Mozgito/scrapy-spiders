import hashlib
import re
import scrapy
from scrapy import Request
from scrapy.utils.python import to_bytes
from scrapy_playwright.page import PageMethod
from ..items import ProductsCrawlerItem


def abort_request(request):
    return request.method.lower() == "post"


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderShopee(scrapy.Spider):
    name = "spider_shopee"
    urls = ["https://shopee.ph/Shoulder-Bags-cat.11021933.11021942"]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", "div.shopee-search-item-result__item > a"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("wait_for_timeout", 2000),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("wait_for_timeout", 2000),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("wait_for_timeout", 2000),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("evaluate", "window.scrollBy(0, 250)"),
            PageMethod("wait_for_timeout", 1000),
        ],
        "errback": errback
    }

    def start_requests(self):
        for url in self.urls:
            yield Request(
                url + "?page=0",
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        next_page = response.xpath(".//span[@class='shopee-mini-page-controller__current']/text()").get()
        total_pages = response.xpath(".//span[@class='shopee-mini-page-controller__total']/text()").get()
        new_url = re.search(r"(https.*?page=)", response.url).group(1)

        products = response.selector.xpath(".//div[@class='row shopee-search-item-result__items']/"
                                           "div[@class='col-xs-2-4 shopee-search-item-result__item']")
        for product in products:
            item_url = re.search(r"(.*?)\?", product.xpath("./a/@href").get())
            if item_url is not None:
                item_url = "https://shopee.ph" + item_url.group(1)
            else:
                item_url = "https://shopee.ph" + product.xpath("./a/@href").get()

            item = ProductsCrawlerItem()
            item['prod_id'] = hashlib.sha1(to_bytes(item_url)).hexdigest()
            item['name'] = product.xpath("./a/div/div/div[@class='ScPA3O']/div[@class='klCFph']/div/div/text()").get() \
                .replace('\n', '').replace('\t', '')
            item['url'] = item_url
            item['price'] = product.xpath("./a/div/div/div[@class='ScPA3O']/div[@class='AQ4KLF']/"
                                          "div[@class='cbl0HO MUmBjS']/span[@class='du3pq0']/text()").get()
            item['currency'] = 'PHP'
            item['image_urls'] = [product.xpath("./a/div/div/div[1]/div/img/@src").get()]
            item['site'] = 'Shopee'
            item['type'] = 'bags'

            yield item

        if next_page < total_pages:
            yield Request(
                new_url + next_page,
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )
