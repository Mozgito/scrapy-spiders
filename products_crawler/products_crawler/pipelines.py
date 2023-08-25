# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes


def str_to_number(str_price) -> [int, float]:
    if '.' in str_price and str_price.rsplit('.', 1)[1].lower() not in ["0", "00"]:
        return float(str_price)

    return int(float(str_price))


class ProductsCrawlerPipeline:
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["prod_id"] in self.ids_seen:
            raise DropItem(f"Duplicate item found: id={adapter['prod_id']}, url={adapter['url']!r}")
        else:
            self.ids_seen.add(adapter["prod_id"])
            return item


class CustomImageNamePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f"{item['type']}/{item['site']}/{image_guid}.jpg"


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGODB_URI"),
            mongo_db=crawler.settings.get("MONGODB_DB", "products_crawler")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            if isinstance(item["price"], str):
                item["price"] = str_to_number(item["price"])

            item_as_dict = ItemAdapter(item).asdict()

            if self.db[item["type"]].find_one_and_update(
                    {"prod_id": item_as_dict["prod_id"], "site": item_as_dict["site"]},
                    {"$set": item_as_dict}
            ) is None:
                self.db[item["type"]].insert_one(item_as_dict)

            return item
        except Exception as err:
            pass
