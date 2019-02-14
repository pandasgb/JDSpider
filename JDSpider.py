"""
@Author:pandasgb
"""

#===========import=============
from requests import get
from time import sleep
import time
import pandas as pd
import re
import json
import os
#==============================

class JDCommentSpider:
    def __init__(self, productId=None, scores=[0, 1, 2, 3, 4, 5, 7]):
        self.productId = str(productId)
        self.scores = scores
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        self.productIdDict = {
            '7652143': 'Xiaomi 8',
        }

    def run(self):
        names = self.productIdDict.get(self.productId, self.productId)
        contentAll = []
        print(names, 'StartTime:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        for score in self.scores:
            pageCount = 0
            while 1:
                sleep(0.5)
                try:
                    txt = parse_comment_page(self, pageCount, score)
                    if not txt.empty:
                        contentAll.append(txt)
                        pageCount += 1
                    else:
                        print(score, pageCount, 'Find no content')
                        break
                except:
                    print('request fail waiting for 2s')
                    sleep(2)
                    pageCount += 1
                    continue
        final_df = pd.concat(contentAll, ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['content'])
        fileDir = 'C:/Users/Administrator/Desktop/JD'
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        final_df.to_csv(fileDir + '/' + str(names) + '.csv', encoding='utf-8-sig', index=False)
        print('EndTime:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def parse_comment_page(self, pagenum, score):
    commenturl = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv15828&productId=' + self.productId + '&score=' + str(
        score) + '&sortType=5&page=' + str(pagenum) + '&pageSize=10&isShadowSku=0&fold=1'
    rs = get(commenturl, headers=self.headers)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), commenturl)
    r = rs.text
    s = re.search("\(", r).span()[1] if re.search('\(', r).span()[1] else 0
    r = r[s:-2]
    r = json.loads(r)
    comments = r['comments']
    tmp_list = []
    for com in comments:
        tmp_list.append(
            [com['id'], com['guid'], com['content'], com['productColor'], com['productSize'], com['creationTime'],
             com['referenceId'], com['referenceTime'], com['score'], com['nickname'], com['userLevelName'],
             com['isMobile'], com['userClientShow']])
    df = pd.DataFrame(tmp_list, columns=['comment_id', 'guid', 'content', 'productColor', 'productSize',
                                         'create_time', 'reference_id', 'reference_time', 'score', 'nickname',
                                         'user_level', 'is_mobile', 'user_client'])
    return df


if __name__ == "__main__":
    productId = 7437788
    spider = JDCommentSpider(productId)
    spider.run()
