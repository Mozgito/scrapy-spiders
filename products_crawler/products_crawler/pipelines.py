# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


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


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGODB_URI"),
            mongo_db=crawler.settings.get("MONGODB_DB")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            item_as_dict = ItemAdapter(item).asdict()
            if self.db[item["type"]].find_one_and_update(
                    {"prod_id": item_as_dict["prod_id"], "site": item_as_dict["site"]},
                    {"$set": item_as_dict}
            ) is None:
                self.db[item["type"]].insert_one(item_as_dict)
            return item
        except Exception as err:
            pass
