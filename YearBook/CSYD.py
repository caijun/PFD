# -*- coding: utf-8 -*-
#===============================================================================
#    Automatically download yearbook from China Statistical Yearbooks Database 
#                 (http://tongji.cnki.net/kns55/index.aspx)
#
#                       Version: 1.1.0 (2014-05-28)
#                         Interpreter: Python 3.3
#                      Test platform: Mac OS 10.9.2
#
#                    Author: Tony Tsai, Ph.D. Student
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os, re, glob

def downloadFile(url, localfile):
#     # NOTE the stream = True parameter
#     r = requests.get(url, stream = True)
#     with open(localfile, 'wb') as f:
#         for chunk in r.iter_content(chunk_size = 1024): 
#             if chunk: # filter out keep-alive new chunks
#                 f.write(chunk)
#                 f.flush()
#     f.close()

        # 只有使用浏览器才能处理alert:对不起，请先登录
#     fp = webdriver.FirefoxProfile()
#     fp.set_preference("browser.download.folderList", 1)
#     fp.set_preference("browser.download.manager.showWhenStarting", False)
#     fp.set_preference("browser.download.dir", os.getcwd())
#     fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/msexcel")
#     browser = webdriver.Firefox(firefox_profile = fp)
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : os.getcwd()}
    chromeOptions.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options = chromeOptions)
    browser.get(url)
    try:
        WebDriverWait(browser, 3).until(EC.alert_is_present())

        alert = browser.switch_to_alert()
        alert.accept()
#         print("alert accepted")
    except TimeoutException:
        print("no alert")
        
    # login in cnki
    browser.find_element_by_id("username").send_keys("thlib")
    browser.find_element_by_id("password").send_keys("thlib")
    browser.find_element_by_id("ImageButton1").click()
    browser.close()
    
    # change newest download file name
    newest = max(glob.iglob("*.[Xx][Ll][Ss]"), key = os.path.getctime)
    os.renames(newest, localfile)

def downloadPage(driver):
#     element = driver.find_element_by_xpath("//img[contains(@src, 'excel-t.gif')]/parent::a")
#     url = element.get_attribute('href')
    
    html = driver.page_source
    soup = BeautifulSoup(html)
    # find data table
    table = soup.find('table', {'class':"dhmltable"})
    rows = table.findAll('tr')
    for row in rows:
        cols = row.findAll('td')
        # extract download url
        col = cols[0]
        href = col.find('a', href = True)
        if href is not None:
            url = href['href'].replace("..", "http://tongji.cnki.net/kns55")
            # extract excel filename
            col = cols[1]
            xls = col.get_text().strip()
            # remove unsafe characters to save file
            xls = re.sub(r'[\\/:"*?<>|]+', "", xls)
            # print(type(os.altsep))
            xlsfile = xls + ".xls"
            print(xlsfile)
            # download file
            downloadFile(url, xlsfile)

def downloadYear(driver, url):
    driver.get(url)
    print(driver.title)
     
    # find button for "统计年鉴"
    driver.find_element_by_link_text("统计数据").click()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.dhmltable-biaotou"))
    )
    records = element.text.strip()
    print(records)        
     
    print("=== page: 1 ===")
    downloadPage(driver)
     
    # page numbers
    pages = records.split("  ")[-1].split(" ")
    for page in pages[1:]:
        driver.find_element_by_link_text(page).click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dhmltable-biaotou"))
        )
          
        print("=== page: " + page + " ===")
        downloadPage(driver)

if __name__ == '__main__':
    homedir = os.getcwd()
    print(homedir)
    # base url for 中国经济与社会发展统计数据库
    baseurl = "http://tongji.cnki.net/kns55/navi/"
    
    # 启动真正的浏览器，可能带来两个问题：一是需要的时间较长，二是UI自动化易受干扰、不够稳定
    driver = webdriver.PhantomJS(executable_path='/usr/local/phantomjs-1.9.7/bin/phantomjs')
    # customize the yearbook and the download url
    yearbooks = {'中国交通年鉴': "HomePage.aspx?id=N2013110008&name=YZGJT&floor=1"}
    for yearbook in yearbooks:       
        url = baseurl + yearbooks[yearbook]
        print(url)
        driver.get(url)
        print(driver.title)
    
        html = driver.page_source
        soup = BeautifulSoup(html)
        ul = soup.find('ul', {'class': "list_h"})
        years = ul.findAll('li')
        for year in years:
            href = year.find('a', href = True)
            url = baseurl + href['href']
            # year number
            yn = href.get_text()[0:-1]
            print(yn)
            # make directory based on yearbook name and year number
            outdir = homedir + '/' + yearbook + '/' + yn + '/'
            if not os.path.exists(outdir):
                os.makedirs(outdir)
                
            # change current directory
            os.chdir(outdir)
            # download yearbook
            downloadYear(driver, url)

    driver.quit()