import re
import scrapy
import time
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductBestSellerItem

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


class SpiderAmazonBestSellers(scrapy.Spider):
    name = "spider_amzn_bs"
    urls = [
        "https://www.amazon.com/s?k=Women%27s+Shoulder+Handbags&i=fashion-womens-handbags&rh=n:3421075011&s=exact-aware-popularity-rank",  # Shoulder bags
        "https://www.amazon.com/s?k=Women%27s+Top-Handle+Handbags&i=fashion-womens-handbags&rh=n:2475901011&s=exact-aware-popularity-rank",  # Top-Handle bags
        "https://www.amazon.com/s?k=Women%27s+Crossbody+Handbags&i=fashion-womens-handbags&rh=n:2475899011&s=exact-aware-popularity-rank",  # Crossbody bags
        "https://www.amazon.com/s?k=Women%27s+Tote+Handbags&i=fashion-womens-handbags&rh=n:16977746011&s=exact-aware-popularity-rank",  # Tote bags
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "IMAGES_MIN_HEIGHT": 0,
        "IMAGES_MIN_WIDTH": 0
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", ".s-result-item")
        ]
    }

    def start_requests(self):
        for url in self.urls:
            yield Request(
                "{}&qid={}&page=1&ref=sr_pg_1".format(url, int(time.time())),
                callback=self.parse,
                method="GET",
                dont_filter=True,
                meta=self.meta,
                errback=errback
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        total_products = 0
        products = response.selector.xpath(".//div[@data-csa-c-type='item']")

        for product in products:
            if total_products == 20:
                break

            if product.xpath("./div[@data-component-type='s-impression-logger']").get() is not None or \
                    product.xpath("./div/div/div[2]/"
                                  "div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']/"
                                  "div[1]/a/span[@class='a-price']").get() is None:
                continue

            item = ProductBestSellerItem()
            item['prod_id'] = re.search(r"asin\.1\.(.*?)$", product.xpath("./@data-csa-c-item-id").get()).group(1)
            item['name'] = product.xpath("./div/div/div[2]/"
                                         "div[@class='a-section a-spacing-none a-spacing-top-small s-title-instructions-style']/"
                                         "h2/a/span/text()").get()
            item['url'] = "https://www.amazon.com" \
                          + re.search(r"(.*?)/ref=", product.xpath(".//a[@class='a-link-normal s-no-outline']/@href").get()).group(1)
            item['price'] = product.xpath("./div/div/div[2]/"
                                          "div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']/"
                                          "div[1]/a/span[@class='a-price']/span[@class='a-offscreen']/text()").get()[1:].replace(',', '')
            rating = product.xpath("./div/div/div[2]/div[@class='a-section a-spacing-none a-spacing-top-micro']/"
                                   "div[@class='a-row a-size-small']/span[1]/@aria-label").get()
            item['rating'] = float(re.search(r"(.*?)\sout", rating).group(1)) if rating is not None else None
            reviews = product.xpath("./div/div/div[2]/div[@class='a-section a-spacing-none a-spacing-top-micro']/"
                                    "div[@class='a-row a-size-small']/span[2]/@aria-label").get()
            item['reviews'] = int(reviews.replace(',', '')) if reviews is not None else None
            sales = product.xpath("./div/div/div[2]/div[@class='a-section a-spacing-none a-spacing-top-micro']/"
                                  "div[@class='a-row a-size-base']/span/text()").get()
            item['sales'] = int(re.search(r"(.*?\+) bought", sales).group(1).replace('K', '000').replace('+', '')) \
                if sales is not None else None
            item['category'] = self.set_category(response.url)
            item['currency'] = 'USD'
            item['image_urls'] = [product.xpath(".//a[@class='a-link-normal s-no-outline']/div/img/@src").get()]
            item['site'] = 'Amazon'
            item['type'] = 'bags_bs'
            item['last_updated'] = int(time.time())
            item['date'] = "{}.{}.{}".format(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday)
            if item['sales'] is None:
                continue

            total_products += 1
            yield item

    def set_category(self, url):
        category = re.search(r"rh=n:(\d+)&s=", url).group(1)
        if category == '3421075011':
            return 'Shoulder Bags'
        if category == '2475901011':
            return 'Top-Handle Bags'
        if category == '16977746011':
            return 'Tote Bags'
        if category == '2475899011':
            return 'Crossbody Bags'

        return None
