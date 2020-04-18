FROM python:3.6-buster

COPY script/multithread_url_scraper.py /script/
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
RUN apt-get update \
    && apt-get -y install curl \
    tree

WORKDIR /script
CMD ["python3", "multithread_url_scraper.py"]
