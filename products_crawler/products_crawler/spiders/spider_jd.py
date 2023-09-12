import base64
import cv2 as cv
import os
import pillow_avif
import random
import re
import scrapy
import time
from pathlib import Path
from scrapy import Request
from scrapy_playwright.page import PageMethod
from ..items import ProductItem


class SpiderJD(scrapy.Spider):
    name = "spider_jd"
    urls = [
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5257&ev=3237_165509%5E",
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5259&ev=3237_165509%5E",
        "https://list.jd.com/list.html?cat=1672%2C2575%2C5260&ev=3237_165509%5E"
        # "https://list.jd.com/list.html?cat=1672%2C2575%2C5258&ev=3237_165509%5E",
    ]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
    }
    meta_login = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", "#formlogin")
        ]
    }
    meta_products = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("wait_for_selector", "li.gl-item")
        ]
    }
    captcha_bg_img = str(Path(os.path.abspath(__file__)).parent.parent.parent) + "/images/captcha_bg.png"
    captcha_puzzle_img = str(Path(os.path.abspath(__file__)).parent.parent.parent) + "/images/captcha_puzzle.png"

    def __init__(self, url_number=None, pages=2, *args, **kwargs):
        super(SpiderJD, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        if url_number is not None:
            self.urls = [self.urls[int(url_number)]]

    def start_requests(self):
        yield Request(
            "https://passport.jd.com/new/login.aspx",
            callback=self.login,
            method="GET",
            dont_filter=False,
            meta=self.meta_login,
            errback=self.errback
        )

    async def login(self, response):
        page = response.meta["playwright_page"]
        await page.fill("input#loginname", self.settings.get('JD_LOGIN'))
        await page.fill("input#nloginpwd", self.settings.get('JD_PSWD'))
        await page.click("a#loginsubmit")

        while page.url != "https://www.jd.com/":
            await page.locator("div[class='JDJRV-img-wrap']").wait_for()
            await self.get_captcha_images(page)
            distance = await self.get_captcha_distance()
            slider_button = page.locator('div[class="JDJRV-slide-inner JDJRV-slide-btn"]')
            sb_box = await slider_button.bounding_box()
            assert sb_box is not None
            await page.mouse.move(sb_box["x"] + sb_box["width"] / 2, sb_box["y"] + sb_box["height"] / 2)
            await page.mouse.down()
            await page.mouse.move(sb_box["x"] + distance + sb_box["width"] / 2, sb_box["y"], steps=10)
            await page.wait_for_timeout(random.randint(2300, 3000))
            await page.mouse.up()
            await page.wait_for_timeout(random.randint(2500, 3000))

        for url in self.urls:
            for page in range(1, self.pages):
                yield Request(
                    url + "&page=" + str(page),
                    callback=self.parse,
                    method="GET",
                    dont_filter=True,
                    meta=self.meta_products,
                    errback=self.errback
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

            item = ProductItem()
            item['prod_id'] = product.xpath("@data-sku").get()
            item['name'] = product.xpath("./div/div[@class='p-name p-name-type-3']/a/em/text()").get() \
                .replace('\n', '').replace('\t', '')
            item['url'] = f"https://item.jd.com/{product.xpath('@data-sku').get()}.html"
            item['price'] = product.xpath("./div/div[@class='p-price']/strong/i/text()").get()
            item['currency'] = 'CNY'
            item['image_urls'] = [img_src]
            item['site'] = 'JingDong'
            item['type'] = 'bags'
            item['last_updated'] = int(time.time())

            yield item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    async def get_captcha_images(self, page):
        bg_image = page.locator("//div[@class='JDJRV-bigimg']/img")
        bg_image_src = await bg_image.get_attribute("src")
        bg_image_base64 = re.search(r"^data:image/png;base64,(.*?)$", bg_image_src).group(1)
        with open(self.captcha_bg_img, "wb") as f:
            f.write(base64.b64decode(bg_image_base64))

        puzzle_image = page.locator("//div[@class='JDJRV-smallimg']/img")
        puzzle_image_src = await puzzle_image.get_attribute("src")
        puzzle_image_base64 = re.search(r"^data:image/png;base64,(.*?)$", puzzle_image_src).group(1)
        with open(self.captcha_puzzle_img, "wb") as f:
            f.write(base64.b64decode(puzzle_image_base64))

    async def get_captcha_distance(self) -> int:
        bg = cv.imread(self.captcha_bg_img)
        puzzle = cv.imread(self.captcha_puzzle_img)

        bg_gr = cv.cvtColor(bg, cv.COLOR_BGR2GRAY)
        bg_bl = cv.medianBlur(bg_gr, 1)
        bg_canny = cv.Canny(bg_bl, 155, 450)

        puzzle_gr = cv.cvtColor(puzzle, cv.COLOR_BGR2GRAY)
        puzzle_bl = cv.medianBlur(puzzle_gr, 1)
        puzzle_canny = cv.Canny(puzzle_bl, 450, 450)

        res = cv.matchTemplate(bg_canny, puzzle_canny, cv.TM_CCOEFF)
        _, _, _, max_loc = cv.minMaxLoc(res)

        return round(max_loc[0] * 0.77222)
