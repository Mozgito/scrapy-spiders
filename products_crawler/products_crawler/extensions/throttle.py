import random
import re
from scrapy.extensions.throttle import AutoThrottle


class AutoThrottleWithList(AutoThrottle):
    """ AutoThrottle with a name list so that the spider limits its
    speed only for the sites on the list """
    def __init__(self, crawler):
        self.limit_list = crawler.settings.getlist("LIMIT_DOMAINS")
        super(AutoThrottleWithList, self).__init__(crawler)

    def _adjust_delay(self, slot, latency, response):
        reg = re.search(r'http[s]?://([^/]+).*', response.url)
        res_domain = reg.group(1)

        if res_domain in self.limit_list:
            super(AutoThrottleWithList, self)._adjust_delay(slot, latency, response)
        else:
            slot.delay = random.uniform(1.0, 1.7)
