# Scrapy settings for products_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import dotenv

dotenv.load_dotenv()

BOT_NAME = "products_crawler"

SPIDER_MODULES = ["products_crawler.spiders"]
NEWSPIDER_MODULE = "products_crawler.spiders"
CLOSESPIDER_TIMEOUT = 6300

LOG_LEVEL = "ERROR"
LOG_FILE = "logs/error.log"

# Scrapy Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Proxy
SCRAPEOPS_API_KEY = os.environ["SCRAPEOPS_APIKEY"]
SCRAPEOPS_PROXY_ENABLED = False

# MongoDB uri and database
MONGODB_URI = os.environ["MONGO_URL"]
MONGODB_DB = os.environ["MONGO_DB"]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 10
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "products_crawler.middlewares.ProductsCrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # "products_crawler.middlewares.ProductsCrawlerDownloaderMiddleware": 543,
    "products_crawler.middlewares.UserAgentMiddleware": 100,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapeops_scrapy.middleware.retry.RetryMiddleware": 550,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
    "products_crawler.middlewares.ScrapeOpsProxyMiddleware": 725
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
    "products_crawler.extensions.throttle.AutoThrottleWithList": 100,
    "scrapeops_scrapy.extension.ScrapeOpsMonitor": 500
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "scrapy.pipelines.images.ImagesPipeline": 100,
    "products_crawler.pipelines.ExcludeProductsPipeline": 89,
    "products_crawler.pipelines.DuplicatesPipeline": 90,
    "products_crawler.pipelines.CustomImageNamePipeline": 100,
    "products_crawler.pipelines.MongoPipeline": 200
}

IMAGES_STORE = "images"
IMAGES_MIN_HEIGHT = 200
IMAGES_MIN_WIDTH = 190
IMAGES_EXPIRES = 365
MEDIA_ALLOW_REDIRECTS = True

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 20
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 30
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False
# List of domains for AutoThrottle
LIMIT_DOMAINS = [
    "list.jd.com",
    "storage.jd.com",
    "shopee.ph",
    "www.lazada.com.ph",
    "www.amazon.com",
    "ph.shein.com",
    "temu.com"
]

# List of excluded product ids
EXCLUDE_PRODUCTS = {
    "bags": {
        "Amazon": [
            "amzn1.asin.1.B09V17P78M",
            "amzn1.asin.1.B08XHY2FSK",
            "amzn1.asin.1.B07C7KHBR8",
            "amzn1.asin.1.B07C7KM56R",
            "amzn1.asin.1.B07C7L13SJ",
            "amzn1.asin.1.B07J36NNG4",
            "amzn1.asin.1.B0CBTC8M7Z",
            "amzn1.asin.1.B0BWMLJ54J",
            "amzn1.asin.1.B0B5CTKNJ3",
            "amzn1.asin.1.B0CCH4Y625",
            "amzn1.asin.1.B0CC1X67W2",
            "amzn1.asin.1.B0CC9DKN5K",
            "amzn1.asin.1.B08M5XN58C",
            "amzn1.asin.1.B0CB21M1FH",
            "amzn1.asin.1.B0BRCRNTVW",
            "amzn1.asin.1.B0B4B4PFH5",
            "amzn1.asin.1.B0CB25N9PJ",
            "amzn1.asin.1.B0C9XMKJ11",
            "amzn1.asin.1.B09LCXBZHR",
            "amzn1.asin.1.B0C75J8T7P",
            "amzn1.asin.1.B0CB25Y74V",
            "amzn1.asin.1.B0CBZP769S",
            "amzn1.asin.1.B0B45DGCQQ",
            "amzn1.asin.1.B0CGFXGYWL",
            "amzn1.asin.1.B0BCV64QSJ",
            "amzn1.asin.1.B0BPHB2CD2",
            "amzn1.asin.1.B094JCXM1Y",
            "amzn1.asin.1.B0BNMF6H9X",
            "amzn1.asin.1.B08L4QNJ2S",
            "amzn1.asin.1.B0C9XPSY45",
            "amzn1.asin.1.B0CBNL34LP",
            "amzn1.asin.1.B09YL6DGD8",
            "amzn1.asin.1.B07NY1RH9X",
            "amzn1.asin.1.B099ZN1VRS",
            "amzn1.asin.1.B0B63KDHL2",
            "amzn1.asin.1.B09W5VX7ZF",
            "amzn1.asin.1.B0C8GGXFWM",
            "amzn1.asin.1.B0BK48RMB2",
            "amzn1.asin.1.B09W5YDV7H",
            "amzn1.asin.1.B0B244M9PL",
            "amzn1.asin.1.B08CSM6RLT",
            "amzn1.asin.1.B081D6PVFD",
            "amzn1.asin.1.B09BK3CMN4",
            "amzn1.asin.1.B0B5L1NV4S",
            "amzn1.asin.1.B08RYSP4P3",
            "amzn1.asin.1.B0BY4WCKRZ",
            "amzn1.asin.1.B0BQ269QF7",
            "amzn1.asin.1.B09VPR6F7V",
            "amzn1.asin.1.B0BKFXZFVH",
            "amzn1.asin.1.B09CT8QS3W",
            "amzn1.asin.1.B095H2JV9D",
        ],
        "Lazada": [
            "2341287112",
            "4002733897",
        ]
    }
}

# JingDong
JD_LOGIN = os.environ["JD_LOGIN"]
JD_PSWD = os.environ["JD_PSWD"]

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
