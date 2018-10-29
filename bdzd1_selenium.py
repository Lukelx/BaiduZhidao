# _*_ coding: utf-8 _*_

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
import os

def start_chrome():
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=option)
    driver.start_client()
    return driver

def keywords():
    filename = 'keywords.txt'
    keywords = []
    with open(filename) as file_object:
        for line in file_object:
            kw_cn = line.strip()
            keywords.append(kw_cn)
    return keywords

def origi_url(keyword):
    # keyword encoding & replace
    kw_gbk = str(keyword.encode('gbk')).lstrip("b'").rstrip("'")
    kw = kw_gbk.replace(r'\x', '%')
    # combine url for baiduzhidao & keyword
    base_url = 'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word='
    origi_url = base_url + kw
    return origi_url

def next_urls(origi_url):
    driver.get(origi_url)
    next_urls = []
    next_urls.append(origi_url)
    n_pg_links_sel = driver.find_elements_by_css_selector('div.pager a')
    for sel in n_pg_links_sel[0:1]:
        link = sel.get_attribute('href')
        next_urls.append(link)
    return next_urls

def sub_urls():
    links = driver.find_elements_by_css_selector('a.ti')
    sub_urls = []
    for link in links:
        sub_url = link.get_attribute('href')
        sub_urls.append(sub_url)
    return sub_urls


def answers(sub_url):
    driver.get(sub_url)
    time.sleep(1)
    answers = []
    try:
        best = driver.find_element_by_css_selector('div.best-text').text
        bs1 = best.lstrip('展开全部\n')
        bs2 = bs1.replace('\n\n', '')
        bs3 = bs2.replace('\n', '')
        best_ans = '最佳答案: ' + bs3
        answers.append(best_ans)
    except NoSuchElementException:
        pass
    try:
        qiye_answer = driver.find_element_by_css_selector('div.ec-answer').text
        qy1 = qiye_answer.lstrip('展开全部\n')
        qy2 = qy1.replace('\n\n', '')
        qy_ans = qy2.replace('\n', '')
        answers.append(qy_ans)
    except NoSuchElementException:
        pass
    try:
        if driver.find_element_by_id('show-answer-hide').is_enabled():
            driver.find_element_by_id('show-answer-hide').click()
        if driver.find_element_by_css_selector('div.show-hide-dispute'):
            driver.find_element_by_css_selector('div.show-hide-dispute').click()
    except NoSuchElementException:
        pass
    other_answers_sels = driver.find_elements_by_class_name('answer-text')
    for other in other_answers_sels:
        other_ans = other.text
        other_ans_t1 = other_ans.lstrip('展开全部\n')
        other_ans_t2 = other_ans_t1.replace('\n\n', '')
        other_answer = other_ans_t2.replace('\n', '')
        answers.append(other_answer)
    answers = [a for a in answers if len(a) > 100]
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
        cur_url = origi_url(keyword)
        cur_next_urls = next_urls(cur_url)
        for url in cur_next_urls:
            driver.get(url)
            cur_sub_urls = sub_urls()
            for cur_sub_url in cur_sub_urls:
                cur_answers = answers(cur_sub_url)
                save_txt(cur_answers, keyword)
        time.sleep(1)


driver = start_chrome()
keywords = keywords()
crawler(keywords)
driver.quit()

