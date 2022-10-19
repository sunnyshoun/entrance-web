# 上市公司基本資料
import sys
import urllib.request
import json
import csv
import codecs
from contextlib import closing
import requests

def fetch(query_limit):
    url = 'https://od.cdc.gov.tw/acute/covid19_vac_hosp.csv'
    req = urllib.request.urlopen(url)

    # 確認資料庫編碼 (utf-8)
    charset = req.info().get_content_charset()
    # print('資料庫編碼:', charset)
    json_data = []

    columns = ('院所名稱', '縣市', '鄉鎮', '疫苗種類', '醫事機構代碼', '地址', '電話')
    col_len=len(columns)
    
    with closing(requests.get(url, stream=True)) as r:
        csv_data = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        for row in csv_data:
            adict = {}
            for i in range(col_len):
                if columns[i] == '疫苗種類':
                    if row[i] == 'AstraZeneca':
                        adict[columns[i]] = row[i]+'（AZ）'
                    elif row[i] == 'Moderna':
                        adict[columns[i]] = row[i]+'（莫德納）'
                    elif row[i] == 'BioNTech':
                        adict[columns[i]] = row[i]+'（BNT）'
                    else:
                        adict[columns[i]] = row[i]
                else:
                    adict[columns[i]] = row[i]
            json_data.append(adict)
            
    if query_limit != 0:
        json_data = json_data[:query_limit]
    return json_data

if __name__ == '__main__':
    json_data = fetch()
    print(json_data)
    