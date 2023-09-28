## Release Notes

### Latest Changes
* 1688 scraper

### 1.5.2
* Switch Temu to US
* Switch Shein to US
* Refactor image resize tool, make square by bigger side
* Add Mongo container limits
* Add two DB indexes: prod_id+site and images.path

### 1.5.1
* Add JD login and captcha solver
* Update requirements
* Add "last_updated" field for item
* Refactor Amazon product id

### 1.5.0 
* Add url selector and max pages count arguments to spiders
* Saving prices as int or float
* Add CRON example
* Temu scraper
* Add excluded product ids list
* Spiders improvements
* Add ScrapeOps Proxy

### 1.4.4
* Shein scraper
* Minor improvements
* Add Changelog

### 1.4.3
* Amazon scraper
* Refactor Shopee scraper
* Refactor Image resize tool
* Update requirements
* Request delays improvements

### 1.4.0
* Shopee scraper
* Lazada scraper
* Image resize tool
* Refactor images structure
* Currency field for product
* Minor fixes

### 1.3.2
* Image cleaner tool
* Custom logger

### 1.3.0
* User-Agent generator
* Custom request throttling

### 1.2.0
* Save products in Mongo DB in Docker

### 1.1.0
* Use Playwright

### 1.0.0
* Project runs on venv, Python 3.8.10
* Scraping products from JD to json file
