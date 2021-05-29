import requests
import argparse
import sys
from bs4 import BeautifulSoup

class Clone(object):

    def __init__(self, arg):
        self.engine = 'https://www.google.com'
        self.searchURI = '/search?num=100&q='
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                                                                                    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Charset":
                                                                                    "ISO-8859-1,utf-8;q=0.7,*;q=0.3", "Accept-Encoding": "none", "Accept-Language":
                                                                                    "en-US,en;q=0.8", "Connection": "keep-alive"}
        self.arg = arg
        if self.arg.tor:
            self.proxies = dict(http='socks5://'+self.arg.tor, https='socks5://'+self.arg.tor)
        else:
           self.arg.tor = 'normal'        
        self.domain = 'https://github.com'
        self.patt = arg.string


    def getPage(self, url):
        if self.arg.tor:
            request = requests.get(url, headers=self.headers, proxies=self.proxies)
        else:
            request = requests.get(url, headers=self.headers)
        bsobj = BeautifulSoup(request.text, "html.parser")
        print(bsobj)
        if bsobj.findAll('a')[-1]['href'].strip('//') == 'support.google.com/websearch/answer/86640':
            sys.exit(
                "\nGoogle has perceived that your are poking around its search engine and it is blocking you!!! Wait "
                "for some time to try again through this network.\n\n")
        return bsobj

    def getNPages(self, response):
        nextpages = response.findAll('a', {'id': 'pnnext'})
        urlnplist = [self.engine + item['href'] for item in nextpages if item.span is not None]
        return urlnplist

    def getRepos(self, response):
        udocument = response.findAll('div', {'class': 'g'})
        urldlist = [item.a['href'] for item in udocument]
        return urldlist


    def do(self):
        url = self.engine+self.searchURI+self.patt+"site:" + self.domain + " ext:" + self.arg.ext
        response =  self.getPage(url)
        repos = self.getRepos(response)
        if repos:
            allPages = self.getNPages(response)
            if allPages:
                nextResponse = self.getPage(allPages[-1])
                nextPages = [page for page in self.getNPages(nextResponse) if not page in allPages]
                if nextPages:
                    allPages = nextPages + allPages
                for page in allPages:
                    resp = self.getPage(page)
                    repos += self.getRepos(resp)
        else:
            sys.exit("\nIt seems you are unlucky!!\n")
        print(len(repos))





    def main(input):
        sys.stdout.write('\n')
        clone = Clone(input)
        clone.do()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="clone.py")
    parser.add_argument('-s', '--string',  help='a string to be searched', required=True, metavar='www.example.com')
    parser.add_argument('-e', '--ext', help='an extension to be seached within github (default: py)', default='py', metavar='java')
    parser.add_argument('-o', '--output', help='a folder path for the git clone output. Default is local (./)', metavar='/path/to/output/')
    parser.add_argument('-t', '--tor', help='an option to specify tor usage (default: non-tor usage)', metavar='host:'
                                                                                                               'port')
    arguments = parser.parse_args()
    Clone.main(arguments)