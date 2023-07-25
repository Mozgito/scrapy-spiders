import pillow_avif
import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductsCrawlerItem


class SpiderJD(scrapy.Spider):
    name = "spider_jd"
    urls = ["https://list.jd.com/list.html?cat=1672%2C2575%2C5259"]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }

    def start_requests(self):
        for url in self.urls:
            for page in range(1, 100):
                yield Request(
                    url + "&page=" + str(page),
                    callback=self.parse,
                    method="GET",
                    dont_filter=True,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "li.gl-item"),
                            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                            PageMethod("wait_for_selector", "li.gl-item:nth-child(60)"),
                        ],
                        "errback": self.errback
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
            item['image_urls'] = [img_src]
            item['site'] = 'JingDong'
            item['type'] = 'bags'

            yield item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
