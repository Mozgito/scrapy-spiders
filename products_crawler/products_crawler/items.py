# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    prod_id = scrapy.Field()
    name = scrapy.Field(serializer=str)
    url = scrapy.Field(serializer=str)
    price = scrapy.Field()
    currency = scrapy.Field(serializer=str)
    image_urls = scrapy.Field()
    images = scrapy.Field()
    site = scrapy.Field(serializer=str)
    type = scrapy.Field(serializer=str)
    last_updated = scrapy.Field(serializer=int)
    pass
