import re
import scrapy
import time
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductItem

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
        "https://www.amazon.com/s?k=Women%27s+Shoulder+Handbags&i=fashion-womens-handbags&rh=n:3421075011,p_n_material_browse:17037742011|17037743011|3388479011",   # Shoulder bags
        "https://www.amazon.com/s?keywords=Women%27s+Top-Handle+Handbags&i=fashion-womens-handbags&rh=n:2475901011,p_n_material_browse:17037742011|17037743011|3388479011",  # Top-Handle bags
        "https://www.amazon.com/s?keywords=Women%27s+Crossbody+Handbags&i=fashion-womens-handbags&rh=n:2475899011,p_n_material_browse:17037742011|17037743011|3388479011",  # Crossbody bags
        "https://www.amazon.com/s?i=fashion-womens-handbags&rh=n:16977746011,p_n_material_browse:17037742011|17037743011|3388479011",  # Tote bags
        "https://www.amazon.com/s?i=fashion-womens-handbags&rh=n:16977748011,p_n_material_browse:17037742011|17037743011|3388479011",  # Satchel bags
        "https://www.amazon.com/s?i=fashion-womens-handbags&rh=n:16977747011,p_n_material_browse:17037742011|17037743011|3388479011"  # Hobo bags
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

            item = ProductItem()
            item['prod_id'] = re.search(r"asin\.1\.(.*?)$", product.xpath("./@data-csa-c-item-id").get()).group(1)
            item['name'] = product.xpath("./div/div/div[2]/"
                                         "div[@class='a-section a-spacing-none a-spacing-top-small s-title-instructions-style']/"
                                         "h2/a/span/text()").get()
            if re.search(r"(cosmetic)|(replacement)", item['name'].lower()) is not None:
                continue

            item['url'] = "https://www.amazon.com" \
                          + re.search(r"(.*?)/ref=", product.xpath(".//a[@class='a-link-normal s-no-outline']/@href").get()).group(1)
            item['price'] = product.xpath("./div/div/div[2]/"
                                          "div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']/"
                                          "div[1]/a/span[@class='a-price']/span[@class='a-offscreen']/text()").get()[1:].replace(',', '')
            item['currency'] = 'USD'
            item['image_urls'] = [product.xpath(".//a[@class='a-link-normal s-no-outline']/div/img/@src").get()]
            item['site'] = 'Amazon'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            yield item

        if next_page <= total_pages and next_page <= self.pages:
            yield Request(
                "{}&qid={}&page={}&ref=sr_pg_{}".format(new_url, int(time.time()), next_page, next_page),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta
            )
