# -*- coding: utf-8 -*-
"""
Created on Thu Jun 02 10:59:45 2016

@author: wenqiang.zwq
"""

# -*- coding: utf-8 -*-
""" 百度贴吧帖子抓取
"""
import urllib2
from pymongo import MongoClient
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
client = MongoClient('localhost', 27017)
db = client['bdtb']
collection = db['tb']

tb = '四川大学'  # 设置要抓取的贴吧

ANSWER_MIN_LEN = 3
ANSWER_MAX_LEN = 100

def get_max_page(tb_name):
    url = "http://tieba.baidu.com/f?kw=%s&pn=1" %tb_name
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, 'lxml')
    last_href_tag = soup.find('a',text = "尾页")
    last_href = last_href_tag['href']
    max_page = int(last_href[last_href.index('pn=')+3:])
    return max_page

def get_page_tb_info(tb_name, page_id):
    url = "http://tieba.baidu.com/f?kw=%s&pn=%s" % (tb_name, page_id)
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, 'lxml')
    li_tag = soup.findAll('li', class_=' j_thread_list clearfix')
    for cur_li_tag in li_tag:
        if cur_li_tag.find('span', title='回复').text == u'0':
            continue
        a_tag = cur_li_tag.find('a', target = '_blank', class_= 'j_th_tit')
        tz_info = {}
        tz_info['tz_id'] = a_tag['href'][3:]
        tz_info['title'] = a_tag['title']
        tz_info['response'] = get_tz_response(tz_info['tz_id'])
        if len(tz_info['response']) > 0:
            collection.insert_one(tz_info)

def get_tz_response(tz_id):
    tz_url = 'http://tieba.baidu.com/p/%s' % tz_id
    html = urllib2.urlopen(tz_url).read()
    soup = BeautifulSoup(html, 'lxml')
    response_div_tag = soup.findAll('div', class_='d_post_content j_d_post_content  clearfix')
    response_list = []
    if 0 == len(response_div_tag):
        return response_list
    else:
        for cur_response_tag in response_list:
            cur_response_text = cur_response_tag.text
            if len(cur_response_text) <= ANSWER_MAX_LEN and len(cur_response_text) >= ANSWER_MIN_LEN:
                response_list.append(cur_response_text)
        return response_list
 
if __name__ == "__main__":
    
    client.close()