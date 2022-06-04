from tracemalloc import start
from urllib import response
from itsdangerous import exc
import requests
from bs4 import BeautifulSoup
import time
from CommentJudge import CommentJudge
import jieba
import json
import os

class PTTCrawler():
    def __init__(self, board, startURL='index.html'):
        self.board = board
        self.startURL = startURL
        self.judge = CommentJudge()
        if requests.get('https://www.ptt.cc/bbs/{}/index.html'.format(self.board)).status_code != 200:
            raise Exception("No board in PTT named {}".format(self.board))
    
    def getPosts(self, number=100000):
        url = 'https://www.ptt.cc/bbs/{}/{}'.format(self.board, self.startURL)
        
        if os.path.isfile('train.json'):
            with open('train.json') as fp:
                ans = json.load(fp)
                counter = len(ans)
        else:
            ans = []
            counter = 0

        while counter < number:
            print(url)
            response = requests.get(url, headers={'cookie': 'over18=1;'})
            if response.status_code == 200:
                # 取得文章的標題和URL，並進一步 call getComments() 取得推文
                root = BeautifulSoup(response.text, 'html.parser')
                posts = root.find_all('div', class_='r-ent')
                for post in posts:
                    link = post.find("a")
                    if link:                        # 如果被刪文，則會是 None
                        if "[問卦] " in link.text and "Re:" not in link.text:
                            counter += 1

                            comments = self.getComments(link.get('href'))
                            if len(comments) != 0:
                                bestComment, score = self.judge.getBest(comments)
                                ans.append({
                                    "Q": link.text.replace('[問卦] ', ''),
                                    "A": bestComment
                                })
                                print(ans[-1], counter)
                                time.sleep(2.5)
                                if counter % 100 == 0:
                                    with open('train.json', 'w') as fp:
                                        json.dump(ans, fp)
                
                # 取得上一頁的位址
                btns = root.find_all('a', class_='btn wide')
                for btn in btns:
                    if '上頁' in btn.text:
                        url = 'https://www.ptt.cc{}'.format(btn.get('href'))
                        print(url)
                        print()
                # time.sleep(3)
            else:
                raise Exception("Response status code {}".format(response.status_code))
        return ans

    def getComments(self, url):
        url = 'https://www.ptt.cc{}'.format(url)
        ans = []
        response = requests.get(url, headers={'cookie': 'over18=1;'})
        root = BeautifulSoup(response.text, 'html.parser')
        comments = root.find_all('div', class_='push')
        for comment in comments:
            try:
                text = comment.find_all('span')[2].text
                if 'http' not in text:
                    ans.append(text.replace(': ', ''))
            except:
                print(comment)  # 推文太多會出現 error
        return ans
