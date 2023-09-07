import re
import scrapy
import time
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductsCrawlerItem

BLOCK_RESOURCE_TYPES = [
    "beacon",
    "font",
    "script",
    "xhr",
    "fetch",
    "ping"
]

BLOCK_RESOURCE_NAMES = [
    "ads.stickyadstv.com",
    "yahoo.com",
    "bs.serving-sys.com",
    "cookie-matching.mediarithmics.com",
    "match.360yield.com",
    "facebook",
    "t.myvisualiq.net",
    "us-u.openx.net",
    "spotxchange.com",
    "fontawesome",
    "google",
]


def abort_request(request):
    if request.method.lower() == "post" or \
            any(key in request.resource_type for key in BLOCK_RESOURCE_TYPES) or \
            any(key in request.url for key in BLOCK_RESOURCE_NAMES):
        return True

    return False


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderAmazon(scrapy.Spider):
    name = "spider_amzn"
    urls = [
        "https://www.amazon.com/s?k=PU+Leather+bag&i=fashion-womens-handbags&rh=n%3A3421075011&s=exact-aware-popularity-rank",  # Shoulder
        "https://www.amazon.com/s?k=PU+leather+bag&i=fashion-womens-handbags&rh=n%3A2475901011&s=exact-aware-popularity-rank",  # Top-Handle
        "https://www.amazon.com/s?k=PU+Leather+bag&i=fashion-womens-handbags&rh=n%3A16977746011&s=exact-aware-popularity-rank"  # Tote
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", ".s-result-item"),
        ],
        "errback": errback
    }

    def __init__(self, url_number=None, pages=1, *args, **kwargs):
        super(SpiderAmazon, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            yield Request(
                "{}&qid={}&page=1&ref=sr_pg_1".format(url, int(time.time())),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        next_page = int(response.xpath(".//span[@class='s-pagination-strip']"
                                       "/span[@class='s-pagination-item s-pagination-selected']/text()").get()) + 1
        total_pages = int(response.xpath(".//span[@class='s-pagination-strip']"
                                         "/span[@class='s-pagination-item s-pagination-disabled']/text()").get())
        new_url = re.search(r"(https.*?qid=)", response.url).group(1)
        products = response.selector.xpath(".//div[@data-csa-c-type='item']")

        for product in products:
            if product.xpath("./div[@data-component-type='s-impression-logger']").get() is not None or \
                    product.xpath("./div/div/div[2]/"
                                  "div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']/"
                                  "div[1]/a/span[@class='a-price']").get() is None:
                continue

            item = ProductsCrawlerItem()
            item['prod_id'] = product.xpath("./@data-csa-c-item-id").get()
            item['name'] = product.xpath("./div/div/div[2]/"
                                         "div[@class='a-section a-spacing-none a-spacing-top-small s-title-instructions-style']/"
                                         "h2/a/span/text()").get()
            item['url'] = "https://www.amazon.com" \
                          + re.search(r"(.*?)/ref=", product.xpath(".//a[@class='a-link-normal s-no-outline']/@href").get()).group(1)
            item['price'] = product.xpath("./div/div/div[2]/"
                                          "div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']/"
                                          "div[1]/a/span[@class='a-price']/span[@class='a-offscreen']/text()").get()[1:].replace(',', '')
            item['currency'] = 'USD'
            item['image_urls'] = [product.xpath(".//a[@class='a-link-normal s-no-outline']/div/img/@src").get()]
            item['site'] = 'Amazon'
            item['type'] = 'bags'

            yield item

        if next_page <= total_pages and next_page <= self.pages:
            yield Request(
                "{}&qid={}&page={}&ref=sr_pg_{}".format(new_url, int(time.time()), next_page, next_page),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )
