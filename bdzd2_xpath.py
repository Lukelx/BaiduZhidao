# _*_ coding: utf-8 _*_

import requests
from urllib.parse import quote
from lxml import etree
import time
import datetime
import os

def keywords():
    filename = 'keywords.txt'
    keywords = []
    with open(filename) as file_object:
        for line in file_object:
            kw = line.strip()
            keywords.append(kw)
    return keywords

def original_url(keyword):
    base_url = 'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word='
    original_url = base_url + quote(keyword)
    return original_url

# transfer '%E7%A6%BB' to bytes and replace '\\' and decode to Chinese
# t0 = (select_sub_urls[0]).split('&')[1].lstrip('word=').replace('%', r'\x')
# tt = bytes(t0, encoding='utf8')
# ttt = eval(repr(tt).replace('\\\\', '\\'))
# print(ttt.decode('utf8'))

def page_urls(original_url):
    page_urls = []
    response1 = requests.get(original_url)
    response1.encoding = 'gbk'
    html1 = etree.HTML(response1.text)
    select_pages = html1.xpath('//*[@class="pager"]/a/@href')
    page_urls.append(original_url)
    for p in select_pages[0:1]:
        p_u = 'https://zhidao.baidu.com' + p
        page_urls.append(p_u)
    return page_urls

def sub_urls(page_url):
    sub_urls = []
    response2 = requests.get(page_url)
    response2.encoding = 'gbk'
    html2 = etree.HTML(response2.text)
    select_sub_urls = html2.xpath('//*[@id="wgt-list"]/dl/dt/a/@href')
    for sel in select_sub_urls:
        sub_urls.append(str(sel))
    return sub_urls

def answers(sub_url):
    answers = []
    response3 = requests.get(sub_url)
    response3.encoding = 'gbk'
    html3 = etree.HTML(response3.text)
    raw_best_answer = html3.xpath('//*[contains(@class, "best-text")]/text()')
    # list joined to string ''.join()
    best_answer = '最佳答案：' + ''.join(raw_best_answer).lstrip("'\n'")
    answers.append(best_answer)
    # obtain other answers' xpath elements
    answer_selectors = html3.xpath('//*[contains(@class, "answer-text")]')
    for ans_sel in answer_selectors:
        # extract other answers' text
        raw_ans = ans_sel.xpath('string(.)')
        oth_ans = raw_ans.replace('展开全部', '').strip('\n')
        answers.append(oth_ans)
    answers = [a for a in answers if len(a) >= 100]
    return answers

def save_txt(answers, keyword):
    folder_name = str(datetime.date.today())
    path = './' + folder_name
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_name = keyword + '.txt'
    for answer in answers:
        if os.path.exists(path + '/' + file_name):
            with open(path + '/' + file_name, 'a', encoding='gbk', errors='ignore') as f:
                f.write(answer)
                f.write('\n' + '=' * 50 + '\n')
        else:
            with open(path + '/' + file_name, 'w', encoding='gbk', errors='ignore') as f:
                f.write(answer)
                f.write('\n' + '=' * 50 + '\n')

def crawler(keywords):
    for keyword in keywords:
        origi_url = original_url(keyword)
        p_urls = page_urls(origi_url)
        for p_url in p_urls:
            s_urls = sub_urls(p_url)
            time.sleep(1)
            for s_url in s_urls:
                cur_answers = answers(s_url)
                save_txt(cur_answers, keyword)


keywords = keywords()
crawler(keywords)