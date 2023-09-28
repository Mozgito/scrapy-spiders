import re
import scrapy
import time
from scrapy import Request, Selector
from scrapy_playwright.page import PageMethod
from ..items import ProductItem


BLOCK_RESOURCE_TYPES = [
    "fetch",
    "font",
    "image",
    "ping",
]


def abort_request(request):
    return any(key in request.resource_type for key in BLOCK_RESOURCE_TYPES)


class Spider1688(scrapy.Spider):
    name = "spider_1688"
    urls = [
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a260j.12536050.jr60bfo3.19.712b52dam0rvqR&&sceneSetId=872&sceneId=2720&bizId=4966&adsSearchWord=%E5%87%AF%E8%8E%89%E5%8C%85",  # Mariah Carey bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a262eq.12572798.jsczez1k.51.64ec2fb1KFrJ53&sceneSetId=872&sceneId=2709&bizId=4955&adsSearchWord=%E6%B3%A2%E5%A3%AB%E9%A1%BF%E5%8C%85",  # Boston bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a260j.12536050.jr60bfo3.20.712b52dam0rvqR&sceneSetId=872&sceneId=2717&bizId=4963&adsSearchWord=%E6%88%B4%E5%A6%83%E5%8C%85",  # Dior bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a262eq.12572798.jsczez1k.50.64ec2fb1KFrJ53&&sceneSetId=872&sceneId=2706&bizId=4952&adsSearchWord=%E6%89%98%E7%89%B9%E5%8C%85",  # Tote bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a262eq.12572798.jsczez1k.32.3e3c2fb1oW4PvW&sceneSetId=872&sceneId=2710&bizId=4956&adsSearchWord=%E8%B4%9D%E5%A3%B3%E5%8C%85",  # Shell bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a262eq.12572798.jsczez1k.31.3e3c2fb1oW4PvW&&sceneSetId=872&sceneId=2715&bizId=4961&adsSearchWord=%E9%A5%BA%E5%AD%90%E5%8C%85",  # Dumpling bag
        "https://show.1688.com/pinlei/industry/pllist.html?spm=a262eq.12572798.jsczez1k.36.3e3c2fb1oW4PvW&sceneSetId=872&sceneId=2724&bizId=4970&adsSearchWord=%E6%B5%81%E8%8B%8F%E5%8C%85",  # Tassel bag
    ]
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", "div.snRows")
        ]
    }

    def __init__(self, url_number=None, *args, **kwargs):
        super(Spider1688, self).__init__(*args, **kwargs)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        for url in self.urls:
            yield Request(
                url,
                callback=self.parse,
                method="GET",
                dont_filter=False,
                meta=self.meta,
                errback=self.errback
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.evaluate("window.scrollBy(0, 310)")
        await self.check_product_filter(page)
        await page.evaluate("window.scrollBy(0, 2000)")
        await self.scroll_to_bottom(page)

        content = await page.content()
        selector = Selector(text=content)
        products = selector.xpath(".//div[@data-tracker='cate1688-offer']")

        for product in products:
            item = ProductItem()
            item['prod_id'] = int(product.xpath("./@id").get())
            item['name'] = product.xpath(".//div[@class='offer-title']/text()").get()
            item['url'] = re.search(r"(.*?\.html)\?", product.xpath("./a/@href").get()).group(1)
            item['price'] = product.xpath(".//div[@class='offer-desc']//span[@class='alife-bc-uc-number']/text()").get().replace('+', '')
            item['currency'] = 'CNY'
            item['image_urls'] = [product.xpath(".//div[@class='offer-img']/img/@src").get()]
            item['site'] = '1688'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            yield item

    async def check_product_filter(self, page):
        filters = page.locator("div[class='snRow']")
        pu_material = filters.get_by_title("PU女包")
        await self.click_element(page, pu_material)

        type_filter = filters.filter(has_text="款式")
        multiple_types = type_filter.get_by_text("多选")
        await self.click_element(page, multiple_types)

        for type_checkbox in await type_filter.get_by_role("checkbox").all():
            await type_checkbox.set_checked(True)

        confirm_button = type_filter.get_by_text("确定")
        await self.click_element(page, confirm_button)

    async def click_element(self, page, element_locator):
        elem_box = await element_locator.bounding_box()
        assert elem_box is not None
        await page.mouse.move(elem_box["x"] + elem_box["width"] / 2, elem_box["y"] + elem_box["height"] / 2)
        await page.mouse.down()
        await page.mouse.up()

    async def scroll_to_bottom(self, page):
        for i in range(8):
            await page.wait_for_timeout(1500)
            await page.evaluate("window.scrollBy(0, -1500)")
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1000)

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
