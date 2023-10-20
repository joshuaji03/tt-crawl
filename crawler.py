import pandas as pd
import os.path
from datetime import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import TypeError
import datetime
import itertools
from dateutil import parser
opts = Options()
import random
#opts.add_argument("user-agent=Naverbot") #tiktok.com/robots.txt

import numpy as np
import time
import json
import pickle

#opts.add_argument('--headless')
opts.add_argument('--disable-gpu')
#opts.add_argument('--headless=new')
opts.add_experimental_option('excludeSwitches',['enable-logging'])
opts.add_argument('--log-level=3')

# set up the webdriver
driver = webdriver.Chrome(options=opts)

# Helper method to convert numbers
def num_convert(s) -> int:
    s = str(s)
    if s.isnumeric():
        return int(s)
    try:
        if len(s) == 0:
            return 0
        if not s[0].isnumeric():
            return 0
        last = s[len(s)-1]
        n = float(s[0:len(s)-1])
        if last == 'K':
            s = n * 1000
        elif last == 'M':
            s = n * 1000000
        elif last == 'B':
            s = n * 1000000000
        return int(s)

    except IndexError:
        print("value with error is: " + s)
        return 0
    
def func():
    choice = "Wrong"

    while choice.isdigit()==False :
        choice = input("请输入达人近十条视频的平均观看需要达到多少: ")

        if choice.isdigit()==False:
            print("Wrongly entered: ")
        else:
            return int(choice)

def func_2():
    choice = "Wrong"

    while choice.isdigit()==False :
        choice = input("请输入等待爬取多久（最好是10以上）: ")

        if choice.isdigit()==False:
            print("Wrongly entered: ")
        else:
            return int(choice)

def find_avg_views(link):
  driver.get(link)
  time.sleep(3)
  page_source = driver.page_source
  soup = BeautifulSoup(page_source, 'lxml')
  view = soup.find_all('strong', class_='video-count tiktok-dirst9-StrongVideoCount e148ts222')
  views = []

  find_min = min(len(view), 10)

  for i in range(0, find_min):
    views.append(num_convert(view[i].text))

  views = np.array(views)
  views = views[(views>np.quantile(views,0.025)) & (views<np.quantile(views,0.975))].tolist()
  
  hou_bu = 10 - len(views)

  if hou_bu > 0 and find_min == 10:
    find_min = min(10 + hou_bu, len(views))

    for i in range(10, 10 + hou_bu):
      views.append(num_convert(view[i].text))

  return sum(views) / len(views)

def main():
    print('如果需要爬去#hashtag内容，在输入项添加#，example: #music, #comedy, #saudiarabia')
    print('若是爬取search bar项目则不需要添加') 
    tag = input('请输入需要爬取的关键词 (多项爬取使用\',\'隔开): ')
    avg_views = func()
    time_to_scrape = func_2()
    date_to_search = input('请输入日期, 无需要直接回撤, 格式为20xx-xx-xx(年-月-日): ')

    # Get the current date and time
    driver = webdriver.Chrome(options=opts)

    # Convert the date and time to an integer using the timestamp() method


    time_stamp = ''

    if len(date_to_search) != 0:
        DT = parser.parse(date_to_search)

        time_stamp = str(int(DT.timestamp()))
    else:
        time_stamp = datetime.datetime.now()
        time_stamp = str(int(time_stamp.timestamp()))

    tags = tag.split(',')

    tag_to_search = []
    for i in range(1, len(tags) + 1):
        tag_to_search.append(list(itertools.combinations(tags, i)))


    link_to_scrape = []
    for l in tag_to_search:
        for t in l:
            link = 'https://tiktok.com/search?q=' + t[0]
            for i in range(1, len(t)):
                link += '%'
                link += '20'
                link += t[i]
            link += '&t='
            link += time_stamp
            link = link.replace(' ', '')
            link_to_scrape.append(link)

    for link in link_to_scrape:
        driver.get(link)

        time.sleep(7)
        scroll_pause_time = 5
        screen_height = driver.execute_script('return window.screen.height;')
        i = 1

        while True and i <= time_to_scrape:
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
            i += 1
            time.sleep(scroll_pause_time)
            scroll_height = driver.execute_script("return document.body.scrollHeight;")

            if (screen_height) * i > scroll_height:
                break

        view_count = [0]
        names = ['']
        index = 0
        temp_list = {}
        while len(view_count) > 0 and len(names) > 0: # find view_count
            index += 1
            x_path_view = '//*[@id="tabs-0-panel-search_top"]/div/div/div[' + str(index) +']/div[2]/div/div[2]/div/strong'
            view_count = driver.find_elements(By.XPATH, x_path_view)
            views = 0
            if len(view_count) > 0 :
                views = num_convert(view_count[0].text)

            id_name_path = 'search_top-item-user-link-' + str(index)
            names = driver.find_elements(By.ID, id_name_path)
            name = ''
            if len(names) > 0:
                name = names[0].text
            if name not in temp_list.keys():
                temp_list[name] = views
            else:
                view = max(temp_list[name], views)
                temp_list[name] = view

        final_list = {}
        for name in temp_list.keys():
            if temp_list[name] > avg_views:
                scrape_link = 'https://tiktok.com/@' + name
                try:
                    avg_views_now = find_avg_views(scrape_link)
                except:
                    continue
                if avg_views_now >= avg_views:    
                    final_list[scrape_link] = avg_views_now

        print(link)
        print(final_list)



if __name__ == '__main__':
    main()
else:
    print('Not running from main')