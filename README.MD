[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Python](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/)
# scrapy-spiders
Playwright Scrapy app for scraping products and their images 
for further finding similar products by photo.
Images are stored in directory of project and product data stored in MongoDB.
### Features
* MongoDB runs in docker container. Scrapy spiders run in regular/virtual environment.
* Scrapy items have `type` field that will be a `collection name` in DB and a `directory name` for images.
* User-Agent generator for each request.
* Custom auto-throttler. Standard download delay applies to the list of domains (`LIMIT_DOMAINS` in `settings.py`)
* Image cleaner tool to keep image data consistent with product database.
* MongoDB 4.4 used for compatibility with servers that don't support AVX. 
Anyway version can be changed to the most fresh 6 or 7. Dump and restore work fine.
### First-time setup
1. Set Mongo connection data in `.env`
2. Install dependencies with `pip install -r requirements.txt`
3. Install Playwright environment with `playwright install` and dependencies with `playwright install-deps`
4. Build and start MongoDB `docker compose up -d`
5. Run spider
### TODO
- [ ] CRON example
- [ ] DB indexes
- [ ] Proxy