import requests
import random
import argparse
import bs4
import random
import threading
from urlparse import urldefrag, urljoin, urlparse

parser=argparse.ArgumentParser()
parser.add_argument('URL',help="Enter the URL to crawl")
args=parser.parse_args()
url=args.URL

proxy = {}

useragent={'User-Agent':str(random.getrandbits(128))}

urls = [url]
domain = urlparse(url).netloc
visited = []
broken_links = []

print("USER_AGENT = {}".format(useragent))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def pagehandler(pageurl, pageresponse):
    print(bcolors.OKGREEN+ 'Crawling:' + pageurl + ' ({0} bytes)'.format(len(pageresponse.text))+bcolors.ENDC)
    return True

def getlinks(pageurl, pageresponse, domain):
    soup = bs4.BeautifulSoup(pageresponse.text, "html.parser")
    links = [a.attrs.get('href') for a in soup.select('a[href]')]
    links = [urldefrag(link)[0] for link in links]
    links = [link for link in links if link]
    links = [link if bool(urlparse(link).netloc) else urljoin(pageurl, link) for link in links]
    if domain:
        links = [link for link in links if urlparse(link).netloc == domain]
    return links


def crawler():
    sess = requests.session()
    if urls[0] not in broken_links and urls[0] not in visited:
        try:
            response = sess.get(urls[0],proxies=proxy,headers=useragent)
            visited.append(urls[0])
            pagehandler(urls[0],response)
            try:
                links = getlinks(urls[0], response, domain)
                for link in links:
                    if link not in visited and link not in broken_links and link not in urls:
                        urls.append(link)
            except:
                print(urls[0])
                pass
            urls.pop(0)
        except (requests.exceptions.MissingSchema,requests.exceptions.InvalidSchema,requests.exceptions.ConnectionError):
            broken_links.append(urls[0])
            print(bcolors.WARNING + "*FAILED*: " + url+bcolors.ENDC)
            urls.pop(0)

def main():
    while len(urls)>0:
        try:
            crawler()
        except IndexError:
            pass
threads = []

if __name__ == "__main__":
    for i in range(10):
        t = threading.Thread(target=main)
        threads.append(t)
        t.start()
