import pillow_avif
import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductsCrawlerItem

BLOCK_RESOURCE_TYPES = [
    "font",
    "script",
    "xhr",
]


def abort_request(request):
    if request.method.lower() == "post" or \
            any(key in request.resource_type for key in BLOCK_RESOURCE_TYPES):
        return True

    return False


async def errback(failure):
    page = failure.request.meta["playwright_page"]
    await page.close()


class SpiderJD(scrapy.Spider):
    name = "spider_jd"
    urls = [
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5257&ev=3237_165509%5E",
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5259&ev=3237_165509%5E",
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5260&ev=3237_165509%5E"
        # "https://list.jd.com/list.html?cat=1672%2C2575%2C5258&ev=3237_165509%5E",
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }

    def __init__(self, url_number=None, pages=2, *args, **kwargs):
        super(SpiderJD, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            for page in range(1, self.pages):
                yield Request(
                    url + "&page=" + str(page),
                    callback=self.parse,
                    method="GET",
                    dont_filter=True,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "li.gl-item")
                        ],
                        "errback": errback
                    }
                )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        products = response.selector.xpath(".//div[@id='J_goodsList']/ul[@class='gl-warp clearfix']/"
                                           "li[@class='gl-item']")
        for product in products:
            img_src = product.xpath("./div/div[@class='p-img']/a/img/@src").get()

            if img_src is not None:
                img_src = "https:" + img_src
            else:
                img_src = "https:" + product.xpath("./div/div[@class='p-img']/a/img/@data-lazy-img").get()

            item = ProductsCrawlerItem()
            item['prod_id'] = product.xpath("@data-sku").get()
            item['name'] = product.xpath("./div/div[@class='p-name p-name-type-3']/a/em/text()").get() \
                .replace('\n', '').replace('\t', '')
            item['url'] = f"https://item.jd.com/{product.xpath('@data-sku').get()}.html"
            item['price'] = product.xpath("./div/div[@class='p-price']/strong/i/text()").get()
            item['currency'] = 'CNY'
            item['image_urls'] = [img_src]
            item['site'] = 'JingDong'
            item['type'] = 'bags'

            yield item
