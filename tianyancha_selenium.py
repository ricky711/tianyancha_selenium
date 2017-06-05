# -*- coding: utf-8 -*-
#webdriver打开详情网页后改用BeautifulSoup解析网页,原来直接用selenium自带的方法解析网页，但不知道为啥偶尔会报错

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4.element import Tag
import time
from urllib.parse import quote
import csv
import random
import re


#创建webdriver访问的url
def full_url(company):
    url_head = 'http://www.tianyancha.com/search?key='
    url_full = url_head + quote(company) + '&searchType=company'
    return url_full

#获取公司信息link
def get_link(company):
    url_full = full_url(company)
    driver.get(url_full)
    time.sleep(3)
    link=''
    try:
        #获取搜索结果列表，目前只看第一页
        element_company = driver.find_elements_by_class_name('search_right_item')
        for each_result in element_company:
            element_now = each_result.find_element_by_tag_name('a')
            if element_now.text == company:
                link = element_now.get_attribute('href')
                break
            element_history = each_result.find_element_by_class_name('add').find_elements_by_class_name('ng-binding')
            if element_history[0].text == '历史名称' and element_history[1].text == company:
                link = element_now.get_attribute('href')
                break
    except NoSuchElementException:
        link = ''
    return link

def get_info(company):
    info = []
    info.append(company)
    link = get_link(company)
    if link:
        driver.get(link)
        time.sleep(5)
        
        #滑动浏览器至基本信息
        try:
            baseinfo = driver.find_element_by_id('nav-main-baseInfo').location
            driver.execute_script("window.scrollTo({0}, {1})".format(0, baseinfo['y']))
        except (NoSuchElementException,TimeoutException,NoSuchWindowException):
            driver.get(link)
            time.sleep(10)
            baseinfo = driver.find_element_by_id('nav-main-baseInfo').location
            driver.execute_script("window.scrollTo({0}, {1})".format(0, baseinfo['y']))
        
        #点击经营范围的详细
        try:
            driver.find_element_by_class_name('company-content').find_element_by_link_text('详细').click()
        except NoSuchElementException:
            time.sleep(5)
            driver.find_element_by_class_name('company-content').find_element_by_link_text('详细').click()
        
        #BeautifulSoup对网页进行解析
        bsobj = BeautifulSoup(driver.page_source,'lxml')

        #公司名称
        company_name = bsobj.find(class_='company_header_width').span.get_text()
        info.append(company_name)

        #企业背景-基本信息：法人代表、注册资本、注册时间、经营状态
        company_table_1 = bsobj.find(class_='baseInfo_model2017').tbody.find_all('td')
        if company_table_1[0].a != None:
            info.append(company_table_1[0].a.get_text().strip())
        else:
            info.append(company_table_1[0].span.get_text())
        info.append(company_table_1[1].get_text())
        info.append(company_table_1[2].get_text())
        info.append(company_table_1[3].get_text())

        #公司信息2
        company_table_2 = bsobj.find(class_='company-content').find_all('div')
        info_1 = []
        for each in company_table_2:
            a = []
            con = each.contents
            a.append(con[0].replace('：','').strip())
            for each1 in con:
                if type(each1) == Tag:
                    a.append(each1.get_text())
            info_1.append(a)
        info_1.remove(['［ 以上评分结果仅供参考 ］'])
        dic = dict(info_1)
        try:
            info.append('`' + dic['工商注册号'])
        except KeyError:
            info.append('null')
        try:
            info.append('`' + dic['组织机构代码'])
        except KeyError:
                info.append('null')
        try:
            info.append('`' + dic['统一信用代码'])
        except KeyError:
            info.append('null')
        try:
            info.append(dic['企业类型'])
        except KeyError:
            info.append('null')
        try:
            info.append(dic['行业'])
        except KeyError:
            info.append('null')
        try:
            info.append(dic['营业期限'].strip())
        except KeyError:
            info.append('null')
        try:
            info.append(dic['核准日期'].strip())
        except KeyError:
            info.append('null')
        try:
            info.append(dic['登记机关'])
        except KeyError:
            info.append('null')
        try:
            info.append(dic['注册地址'])
        except KeyError:
            info.append('null')
        try:
            info.append(dic['经营范围'].replace('详细','').replace('收起','').strip())
        except KeyError:
            info.append('null')
        
        #评分
        company_table_3 = bsobj.find(class_='company-content').img['ng-alt'].replace('评分','')
        if company_table_3:
            info.append(company_table_3)
        else:
            info.append('0')
    else:
        info_no = ['企业未查得']*16
        info = info + info_no
    return info

#打开浏览器
#不加载图片
options = webdriver.ChromeOptions()
prefs = {
	'profile.default_content_setting_values':{
		'images':2
	}
}
options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(chrome_options=options)
driver.maximize_window()

company='百度'
info = get_info(company)

driver.quit()



