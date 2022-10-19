# 上市公司基本資料
import urllib.request
import requests
from contextlib import closing
import json
import csv
from amaindb import MAINDB
from scraper import ggfinance

mainDB = MAINDB()

def fetch():
    url = 'https://quality.data.gov.tw/dq_download_json.php?nid=18419&md5_url=04541d53fd5cbeb2803e0fe4becc4b97'
    req = urllib.request.urlopen(url)

    # 確認資料庫編碼 (utf-8)
    charset = req.info().get_content_charset()
    # print('資料庫編碼:', charset)

    response_data = json.loads(req.read())
    records = []
    columns = ('公司代號', '公司名稱', '公司簡稱', '董事長', '成立日期', '上市日期')
    for company in response_data:
        adict = {}
        for col in columns:
            adict[col] = company[col]
        records.append(adict)
    return columns, records

def fetch_csv():
    url = 'https://quality.data.gov.tw/dq_download_csv.php?nid=18419&md5_url=04541d53fd5cbeb2803e0fe4becc4b97'
    with closing(requests.get(url, stream=True)) as req:
        records = [line.decode('utf-8') for line in req.iter_lines()]
        atable = csv.reader(records, delimiter=',', quotechar='"')
        for row in atable:
            print(row[1:4])

if __name__ == '__main__':
    columns, records = fetch()
    t=0
    adict = {'selCurrency':'TWD'}
    for i in range(511,len(records)):
        record = records[i]
        adict['txtStockEx'] = record['公司代號']+':TPE'
        adict['txtStockID'] = record['公司代號']
        adict['txtName'] = record['公司簡稱']
        
        stock_info = ggfinance.get_stock_price(adict['txtStockEx'])

        if stock_info[0]:
            adict['txtFullname'] = stock_info[1]['stitle']
            mainDB.save_stock(**adict)
            print(f"第{i+1}筆 成功新增：{adict['txtFullname']}")
        else:
            print(f"第{i+1}筆 無效股票：{adict['txtName']}")
    # print(records)
    # print(json.dumps(records, sort_keys=True, indent=4), file=open('listedcom.json', 'wt'))
    # fetch_csv()
    