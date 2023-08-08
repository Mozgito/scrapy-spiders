import cv2 as cv
import math
import os
from pathlib import Path


def resize_image(image_path: str, size: int) -> None:
    img = cv.imread(image_path, cv.IMREAD_COLOR)
    height = img.shape[0]
    width = img.shape[1]
    preferred_height = size
    preferred_width = size
    pad_top = 0
    pad_bot = 0
    pad_left = 0
    pad_right = 0

    if height > width:
        preferred_width = round(preferred_height / height * width)
        pad_left = math.floor((size - preferred_width) / 2)
        pad_right = math.ceil((size - preferred_width) / 2)

    if height < width:
        preferred_height = round(preferred_width / width * height)
        pad_top = math.floor((size - preferred_height) / 2)
        pad_bot = math.ceil((size - preferred_height) / 2)

    if height != size or width != size:
        img_new = cv.resize(img, (preferred_width, preferred_height))
        img_new_padded = cv.copyMakeBorder(
            img_new,
            pad_top,
            pad_bot,
            pad_left,
            pad_right,
            cv.BORDER_CONSTANT,
            value=[255, 255, 255]
        )
        cv.imwrite(image_path, img_new_padded)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    images_path = str(Path(os.path.abspath(__file__)).parent.parent.absolute()) + "/images/bags/"
    sites = os.listdir(images_path)

    for site in sites:
        for image in os.listdir(images_path + site):
            abs_image_path = os.path.join(images_path, site, image)
            if os.path.isfile(abs_image_path):
                if site in ['Lazada', 'Shopee']:
                    resize_image(abs_image_path, 700)
                else:
                    resize_image(abs_image_path, 350)
