# 高雄市人民團體校友會
import sys
import urllib.request
import json
import csv

def fetch(query_limit):
    # 指定查詢筆數上限
    url = 'https://data.kcg.gov.tw/dataset/f4375239-af26-40f6-8394-d942f3ecf753/resource/ad36b1f2-8a2c-4491-a516-da607bd96c39/download/.json'
    req = urllib.request.urlopen(url)

    # 確認資料庫編碼 (utf-8)
    charset = req.info().get_content_charset()
    # print('資料庫編碼:', charset)

    # 讀取資料
    # response_data = req.read().decode(charset)
    response_data = req.read()

    # 轉成 JSON 格式
    json_data = json.loads(response_data)

    # 依查詢筆數上限設定準備回傳的資料
    json_data = json_data
    if query_limit != 0:
        json_data = json_data[:query_limit]
    return json_data


if __name__ == '__main__':
    qlimit = int(input('設定查詢筆數 (0.all | -1.quit): '))
    if qlimit == -1:
        sys.exit()

    Light_Rail_data = fetch(qlimit)
    print(json.dumps(Light_Rail_data, sort_keys=True, indent=4), file=open('Light_Rail.json', 'wt'))

    # encoding='utf8' (不支援 ASCII)
    # newline='' (若未設定，每列後會再多換一行)
    with open('Light_Rail.csv', 'w', newline='', encoding='utf8') as Light_Rail_csv:
        # 資料寫入檔案
        csvwriter = csv.writer(Light_Rail_csv)
        header = Light_Rail_data[0].keys()
        csvwriter.writerow(header)
        count = 0
        for row in Light_Rail_data:
            count += 1
            csvwriter.writerow(row.values())
    print('\n'+'資料筆數:', count)
    