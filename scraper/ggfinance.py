from scraper import webutils
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def get_stock_price(stockex):
    url = f'https://www.google.com/finance/quote/{stockex}?hl=zh-TW'
    headers = {'User-Agent':webutils.UserAgent}
    req = Request(url, headers=headers)
    html = urlopen(req)
    bsoup = BeautifulSoup(html.read(), 'html.parser')
    stitle = bsoup.find("div", {"role":"heading","aria-level":"1","class": "zzDege"})
    sprice = bsoup.find("div", class_="YMlKec fxKbKc")
    last_price = bsoup.find("div", class_="P6K39c")
    if  None == stitle or None == sprice or None == last_price:
        return (None,None)
    else:
        stitle=stitle.string
        sprice=sprice.string.replace(',','')
        last_price=last_price.string.replace(',','')
        spercent=str(round(((float(sprice[1:])-float(last_price[1:]))/float(last_price[1:]))*100,2))
        return (True,{"stitle":stitle,"sprice":sprice,"spercent":spercent})
    
if __name__ == '__main__':
    print(get_stock_price('2330:TPE'))