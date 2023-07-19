import scrapy
from scrapy import Request

from ..items import ProductsCrawlerItem


class SpiderJD(scrapy.Spider):
    name = 'spider_jd'
    urls = ['']

    headers = {}

    def start_requests(self):
        for url in self.start_urls:
            for page in range(1, 1):
                yield Request(url + '&page=' + page, headers=self.headers, callback=self.parse, method='GET',
                              dont_filter=True)

    def parse(self, response):
        self.log('response url: %s, status: %d' % (response.url, response.status), level=20)

        products = response.selector.xpath(".//div[@id='J_goodsList']/ul[@class='gl-warp clearfix']/"
                                           "li[@class='gl-item']")
        for product in products:
            item = ProductsCrawlerItem()
            item.prod_id = product.attrib("data-sku")  # xpath("@data-sku").get()
            item.name = product.xpath(".//div/div[@class='p-name']/a/em/text()").extract_first().replace('\n', '') \
                .replace('\t', '')
            item.url = f"https://item.jd.com/{product.attrib('data-sku')}.html"
            item.price = product.xpath(".//div/div[@class='p-price']/strong/i/text()").extract_first()
            item.image_urls = "https:" + product.xpath(".//div/div[@class='p-img']/a/img/@src").extract_first()
            item.site = 'jd.com'
            yield item
