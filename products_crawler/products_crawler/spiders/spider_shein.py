import re
import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductsCrawlerItem

BLOCK_RESOURCE_TYPES = [
    "beacon",
    "font",
    "image",
    "xhr",
    "fetch",
    "ping"
]

BLOCK_RESOURCE_NAMES = [
    "facebook",
    "google",
    "googletagmanager",
    "twitter",
    "bing.com",
    "amazonaws.com",
    "riskified.com",
    "forter.com",
    "gstatic.com",
    "srmdata.com",
    "doubleclick.net"
]


def abort_request(request):
    if "api/productAtom/atomicInfo/get" not in request.url and \
            (request.method.lower() == "post" or
             any(key in request.resource_type for key in BLOCK_RESOURCE_TYPES) or
             any(key in request.url for key in BLOCK_RESOURCE_NAMES)):
        return True

    return False


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderShein(scrapy.Spider):
    name = "spider_shein"
    urls = [
        "https://ph.shein.com/Bags-&-Luggage-c-3637.html?attr_values=PU%20Leather&child_cat_id=1764&attr_ids=160_532&exc_attr_id=160",
        "https://ph.shein.com/Bags-&-Luggage-c-3637.html?attr_values=PU%20Leather&child_cat_id=2152&attr_ids=160_532&exc_attr_id=160",
        "https://ph.shein.com/Bags-&-Luggage-c-3637.html?attr_values=PU%20Leather&child_cat_id=2844&attr_ids=160_532&exc_attr_id=160",
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", ".sui-pagination__total"),
        ],
        "errback": errback
    }

    def __init__(self, url_number=None, pages=1, *args, **kwargs):
        super(SpiderShein, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            yield Request(
                url + "&page=1",
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        current_url_regex = re.search(r"(https.*?&page=)(\d+)", response.url)
        new_url = current_url_regex.group(1)
        next_page = int(current_url_regex.group(2)) + 1
        total_pages = int(re.search(r'\d+', response.xpath(".//span[@class='sui-pagination__total']/text()").get())
                          .group(0))

        products = response.selector. \
            xpath(".//section[@class='S-product-item j-expose__product-item product-list__item']")

        for product in products:
            item = ProductsCrawlerItem()
            item['prod_id'] = product.xpath("./div[@class='S-product-item__wrapper']/a/@data-id").get()
            item['name'] = product.xpath("./div[@class='S-product-item__wrapper']/a/@data-title").get()
            item['url'] = "https://ph.shein.com" + re.search(r"(.*?\.html)\?", product.xpath("./div[@class='S-product-item__wrapper']/a/@href").get()).group(1)
            item['price'] = product.xpath(".//span[@class='normal-price-ctn__sale-price normal-price-ctn__sale-price_discount']/@aria-label").get()[6:]
            item['currency'] = 'PHP'
            item['image_urls'] = ["https:" + product.xpath("./div[@class='S-product-item__wrapper']/a/div[1]/@data-before-crop-src").get()]
            if product.xpath("./div[@class='S-product-item__wrapper']/a/div[2]/div").get():
                item['image_urls'].append("https:" + product.xpath("./div[@class='S-product-item__wrapper']/a/div[2]/div/@data-before-crop-src").get())
            item['site'] = 'Shein'
            item['type'] = 'bags'

            yield item

        if next_page <= total_pages and next_page <= self.pages:
            yield Request(
                new_url + str(next_page),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )
