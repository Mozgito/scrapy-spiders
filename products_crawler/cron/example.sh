#!/bin/bash

if [ -z ${1} ] || [ -z ${2} ]
then
  echo "Specify (1) url number and (2) pages count!"
else
  cd /path_to/scrapy-spiders/products_crawler
  PATH=$PATH:/usr/local/bin
  export PATH
  scrapy crawl SPIDER_NAME -a url_number=${1} -a pages=${2}
fi
