import scrapy
from scrapy import Request

from ..items import ProductsCrawlerItem


class SpiderJD(scrapy.Spider):
    name = 'spider_jd'
    urls = ['']

    headers = {
        ":authority": "list.jd.com",
        ":method": "GET",
        ":scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language:": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        for url in self.urls:
            for page in range(1, 100):
                yield Request(url + '&page=' + str(page), headers=self.headers, callback=self.parse, method='GET',
                              dont_filter=True)

    def parse(self, response):
        self.log('response url: %s, status: %d' % (response.url, response.status), level=20)

        products = response.selector.xpath(".//div[@id='J_goodsList']/ul[@class='gl-warp clearfix']/"
                                           "li[@class='gl-item']")
        for product in products:
            img_src = product.xpath("./div/div[@class='p-img']/a/img/@src").get()
            img_data_lazy = "https:" + product.xpath("./div/div[@class='p-img']/a/img/@data-lazy-img").get()

            item = ProductsCrawlerItem()
            item['prod_id'] = product.xpath("@data-sku").get()
            item['name'] = product.xpath("./div/div[@class='p-name p-name-type-3']/a/em/text()").get() \
                .replace('\n', '').replace('\t', '')
            item['url'] = f"https://item.jd.com/{product.xpath('@data-sku').get()}.html"
            item['price'] = product.xpath("./div/div[@class='p-price']/strong/i/text()").get()
            item['image_urls'] = [img_src] if img_src is not None else [img_data_lazy]
            item['site'] = 'jd.com'
            yield item
