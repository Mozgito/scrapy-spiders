import os
import pymongo
from dotenv import load_dotenv
from logger import mylogger
from pathlib import Path


class ImageCleaner:
    def __init__(self):
        load_dotenv()
        self.logger = mylogger(__name__)
        self.client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        self.db = self.client[os.environ.get("MONGO_DB")]
        self.images_path = str(Path(os.path.abspath(__file__)).parent.parent.absolute()) + "/images/bags/"

    def get_images_list_from_db(self) -> list:
        return self.db["bags"].distinct("images.path")

    def get_images_list_from_dir(self) -> list:
        return os.listdir(self.images_path)


image_cleaner = ImageCleaner()
db_list = image_cleaner.get_images_list_from_db()
dir_list = image_cleaner.get_images_list_from_dir()
file_counter = 0

for image in dir_list:
    db_image_name = "bags/" + image
    if db_image_name not in db_list:
        os.remove(image_cleaner.images_path + image)
        file_counter += 1

image_cleaner.logger.info(f"{file_counter} images were deleted.")
