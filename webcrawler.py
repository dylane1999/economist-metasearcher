import json
from collections import defaultdict
from csv import DictWriter

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http.request import Request
import re
import urllib.request, urllib.error, urllib.parse
from datetime import datetime



KEYWORDS_FILE = 'textfile.txt'
SCRAPY_OUTPUT_FILE = 'scrapy-output.json'
RANKED_OUTPUT_FILE = 'output.csv'


def contains_date(url):
    """Returns True if the url contains a date."""
    return bool(re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url))

def extract_date(url):
    """Returns the date in a url."""
    result = re.findall(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
    date = result[0]
    date = ''.join(x for x in date if x not in '()')
    datetimeobject = datetime.strptime(date, '%Y%m%d')
    date = datetimeobject.strftime('%m/%d/%Y')
    return date

class EconomistSpider(scrapy.Spider):

    name = "economist"

    def start_requests(self):
        # see https://stackoverflow.com/a/10379463
        for keyword in read_keywords():
            yield Request('https://www.economist.com/search?q=' + keyword.strip(), self.parse)

    def parse(self, response):
        word = response.url.split('=')[1]
        if '&page' in word:
            word = word.replace('&page', '')
        # yield info requested
        for result in response.css('ol.layout-search-results li'):
            title = result.xpath('string(.//a/h2/span[2])').get()
            if title == '':
                title = result.xpath('string(.//a/h2/span)').get();
            yield {
                'Link': result.css('li a.search-result::attr(href)').get(),
                'title': title,
                'word': word,
            }
        # follow to the next page of that search term
        next_page_params = response.css('li.ds-pagination__nav--next a::attr(href)').get()
        if next_page_params is not None:
            next_page = 'https://www.economist.com/search' + next_page_params
            yield response.follow(next_page, callback=self.parse)


def read_keywords():
    with open(KEYWORDS_FILE) as fd:
        return [keyword.strip() for keyword in fd.readlines()]


def collate():
    # read in results from crawler
    result_keywords = defaultdict(set)
    result_titles = {}
    with open(SCRAPY_OUTPUT_FILE) as fd:
        results = json.load(fd)
    for result in results:
        url = result['Link']
        if contains_date(url):
            result_keywords[url].add(result['word'])
            result_titles[url] = result['title']
    # sort results by the number of keywords matched
    ranked_urls = sorted(result_keywords, key=(lambda url: len(result_keywords[url])), reverse=True)
    # write results
    keywords = read_keywords()
    with open(RANKED_OUTPUT_FILE, 'w') as fd:
        writer = DictWriter(fd, fieldnames=['url', 'title', 'date', 'keywords'])
        writer.writeheader()
        for url in ranked_urls:
            date = extract_date(url)
            writer.writerow({
                'url': url,
                'title': result_titles[url],
                'date': date,
                'keywords': str(', '.join(sorted(result_keywords[url]))),
            })
            download(url)



def download(url):

    if url.find('/'):
        name = url.rsplit('/', 1)[1] # splits url into an array of strings by '/' with a max of one split and then returns the string at index 1

    with urllib.request.urlopen(url) as response:
        webContent = response.read()



    with open(name + ".html", 'w') as fd:
        fd = open(name + ".html", 'wb')
        fd.write(webContent)
        fd.close


def main():
    process = CrawlerProcess(settings={
        'FEEDS': {
            SCRAPY_OUTPUT_FILE: {
                'format': 'json',
            },
        },
    })
    process.crawl(EconomistSpider)
    process.start()
    # the script will block here until the crawling is finished
    collate()


if __name__ == "__main__":
    main()
