# _*_ coding: utf-8 _*_

import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
import os
import datetime


class KeyWords:

    def __init__(self, filename):
        self.filename = filename
        self.keywords = []
        self.import_keywords()

    def import_keywords(self):
        with open(self.filename) as file_object:
            for line in file_object:
                kw = line.strip()
                self.keywords.append(kw)
        return self.keywords


class SubUrls:

    def __init__(self, keyword):
        self.keyword = keyword
        self.sub_urls = []
        self.page_urls()

    def original_url(self):
        base_url = 'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word='
        original_url = base_url + quote(self.keyword)
        return original_url

    def page_urls(self):
        ori_url = self.original_url()
        page_urls = []
        page_urls.append(ori_url)
        response1 = requests.get(ori_url)
        response1.encoding = 'gbk'
        soup1 = BeautifulSoup(response1.text, 'lxml')
        page_urls_tag = soup1.find(class_='pager').find_all('a')
        for p_tag in page_urls_tag[0:1]:
            p_url = 'https://zhidao.baidu.com' + p_tag.get('href')
            page_urls.append(p_url)
        return page_urls

    def get_sub_urls(self):
        p_urls = self.page_urls()
        # print(p_urls)
        for cur_p_url in p_urls:
            response2 = requests.get(cur_p_url)
            response2.encoding = 'gbk'
            soup2 = BeautifulSoup(response2.text, 'lxml')
            sub_urls_tag = soup2.find_all('a', class_='ti')
            for s_u_tag in sub_urls_tag:
                s_url = s_u_tag.get('href')
                self.sub_urls.append(s_url)
        return self.sub_urls


class Answers:

    def __init__(self, sub_url):
        self.sub_url = sub_url
        self.answers = []
        self.get_answers()

    def get_answers(self):
        response3 = requests.get(self.sub_url)
        response3.encoding = 'gbk'
        soup3 = BeautifulSoup(response3.text, 'html5lib')
        time.sleep(1)
        try:
            bs_answer_tag = soup3.find(class_='best-text')
            raw_bs_answer = bs_answer_tag.text
            bs_answer = raw_bs_answer.replace('展开全部', '').strip('\n')
            best_answer = '最佳答案：' + bs_answer
            self.answers.append(best_answer)
        except AttributeError:
            pass
        other_answers_tag = soup3.find_all(class_='answer-text')
        for o_a in other_answers_tag:
            raw_other_answer = o_a.text
            other_answer = raw_other_answer.replace('展开全部', '').strip('\n')
            self.answers.append(other_answer)
        self.answers = [a for a in self.answers if len(a) >= 100]
        return self.answers


class SaveAnswers:

    def __init__(self, keyword, answers):
        self.keyword = keyword
        self.answers = answers
        self.save_answers()

    def save_answers(self):
        folder_name = str(datetime.date.today())
        path = './' + folder_name
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        file_name = self.keyword + '.txt'
        for answer in self.answers:
            if os.path.exists(path + '/' + file_name):
                with open(path + '/' + file_name, 'a', encoding='gbk', errors='ignore') as f:
                    f.write(answer)
                    f.write('\n' + '=' * 50 + '\n')
            else:
                with open(path + '/' + file_name, 'w', encoding='gbk', errors='ignore') as f:
                    f.write(answer)
                    f.write('\n' + '=' * 50 + '\n')


kws = KeyWords(filename='keywords.txt')
for k in kws.keywords:
    sus = SubUrls(k)
    sus.get_sub_urls()
    time.sleep(1)
    for s in sus.sub_urls:
        cur_answers = Answers(s)
        now_save = SaveAnswers(k, cur_answers.answers)

