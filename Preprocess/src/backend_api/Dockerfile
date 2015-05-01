# To build a docker image: docker build -t scrapy_crawler .
# To run scrapy after image is built: docker run -v [directory_to_search_infrastructure_folder]:/search-infrastructure -p 8082:8082 --privileged=true scrapy_crawler sh -c 'source crawler_venv/bin/activate && cd /search-infrastructure/scrapy_crawler/review_crawler/ && scrapy crawl review_crawler -a company=babiesrus'

# Test command on local:
# docker run -v /Users/haoyu/Workspace/search-infrastructure:/search-infrastructure scrapy_crawler sh -c 'source crawler_venv/bin/activate && cd /search-infrastructure/scrapy_crawler/review_crawler/ && scrapy crawl review_crawler -a company=babiesrus'

# Test browsepage crawler on local:
# docker run -v /Users/haoyu/Workspace/search-infrastructure:/search-infrastructure scrapy_crawler sh -c 'source crawler_venv/bin/activate && cd search-infrastructure/crawler/src && python browsePageCrawler.py -c babyworldonline --date 2015-04-08 --Headless'

FROM centos:latest
MAINTAINER Zaicheng Wang <zaicheng.wang@ussuning.com>
ADD requirements* /home/

RUN yum install -y epel-release
RUN yum install -y python-pip

# Create envrionment for Backend-api
RUN pip install -r /home/requirements.txt
