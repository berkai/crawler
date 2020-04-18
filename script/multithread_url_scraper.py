import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import pandas as pd
import time
import csv
import os
queries = []
images = []
data = {}
# timeout = time.time() + 15
search_links = [f"https://www.java.com/en/"]
class MultiThreadScraper:

    def __init__(self, base_url):
        '''
        creating and adding urls to queue
        '''
        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme,
                                         urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=8)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)

    def parse_links(self, html):
        '''
        finder for "href" links inside of html 
        and checks is it scraped before 
        '''
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    self.to_crawl.put(url)


    def scrape_info(self, html):
        return

    def post_scrape_callback(self, res):
        '''
        if http status codde is '200' put that link
        in parse_links function
        '''
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            self.scrape_info(result.text)

    def scrape_page(self, url):
        '''
        trying get url's response via requests
        '''
        try:
            res = requests.get(url, timeout=(3, 30))
            return res
        except requests.RequestException:
            return

    def run_scraper(self):
        '''
        runner for scraper. saves the urls in java.csv
        making dir with using links
        '''
        with open("java.csv", 'a') as file:
            file.write("url")
            file.writelines("\n")
            while True:
                try:
                    target_url = self.to_crawl.get(timeout=15)
                    s = set(self.scraped_pages) # checking string is scraped with set() method is really faster 
                    if target_url not in s:
                        dir_name = target_url.replace('https://', ' ')
                        parent_dir = "./urls_tree"
                        path = os.path.join(parent_dir, target_url) # joins the directory where is it belonga
                        os.makedirs(path, exist_ok = True) # make dirs giving path
                        self.scraped_pages.add(target_url)
                        job = self.pool.submit(self.scrape_page, target_url)
                        job.add_done_callback(self.post_scrape_callback)
                        df = pd.DataFrame([{'url': target_url}])
                        df.to_csv(file, index=False, header=False)
                except Empty:
                    return
                except Exception as e:
                    print(e)
                    continue


if __name__ == '__main__':
    '''
    makes dir to showing results
    if its exists replace it with new one
    run the class with links in search_links list
    than tree will shows site map using the directories
    '''
    try:
        os.makedirs('./urls_tree')
    except FileExistsError as e:
        os.replace('./urls_tree', './urls_tree')
    for link in search_links:
        s = MultiThreadScraper(link)
        s.run_scraper()
    os.system('tree ./urls_tree')
    os.system('tree -H ./ > result.html')
