FROM python:3.8.10-slim

WORKDIR /products_crawler
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY requirements.txt /products_crawler/requirements.txt

#RUN apt-get update && apt-get install -y libgl1 ffmpeg libsm6 libxext6

RUN pip install --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
     --no-cache-dir --timeout 60 -r requirements.txt