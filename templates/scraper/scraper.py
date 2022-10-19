# TOEIC Vocabulary
import webutils
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

url = 'http://englishgrammarpass.com/exercises/all_words/toeic-vocabulary/67.html'
headers = {'User-Agent':webutils.UserAgent}
req = Request(url, headers=headers)
html = urlopen(req)
bsoup = BeautifulSoup(html.read(), 'html.parser')
print(bsoup.title)
print(bsoup.title.string, '\n')
print(bsoup.h1)
print(bsoup.h1.string, '\n')
print(bsoup.h1.span)
print(bsoup.h1.span.string, '\n')
print(bsoup.strong)
print(bsoup.strong.string)
    