# -*- coding: utf-8 -*-
#===============================================================================
# Automatically download weekly influenza report from China National Influenza Center
#                 (http://www.cnic.org.cn/chn/down/?typeid=20)
#
#                       Version: 1.0.0 (2016-05-10)
#                        Interpreter: Python 3.5.1
#                      Test platform: Mac OS 10.11.4
#
#                    Author: Tony Tsai, Ph.D. Candidate
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#          (Center for Earth System Science, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
import os, re, requests

def text2name(text):
    texts = text.strip().split(" ")
    texts[1] = str(int(re.sub('[第|周|期]', '', texts[1]))).zfill(2)
    name = ''.join(texts)
    return(name)

def downloadFile(fileurl, filename):
    req = requests.get(fileurl)
    file = open(filename, 'wb')
    file.write(req.content)
    file.close()
    print("Download PDF Completed")

def downloadPage(driver, pageurl):
    driver.get(pageurl)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # find unordered list of files
    ul = soup.find('ul', {'class':"new_list jianbao"})
    lis = ul.findAll('li')
    for li in lis:
        hrefs = li.findAll('a', href = True)
        if len(hrefs) < 2:
            print(hrefs[0])
            continue
        # http://www.cnic.org.cn/uploadfile/2016/0509/20160509100219176.pdf
        fileurl = "http://www.cnic.org.cn/" + hrefs[0]['href']
        print(fileurl)
        comps = urlparse(fileurl)
        file_name, file_ext = os.path.splitext(os.path.basename(comps.path))
        text = hrefs[1].get_text()
        filename = text2name(text) + file_ext
        print(filename)
        downloadFile(fileurl, filename)

if __name__ == '__main__':
    homedir = os.getcwd()
    print(homedir)
    # base url for 流感周报
    baseurl = "http://www.cnic.org.cn/chn/down/?typeid=20"
    
    driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
    driver.get(baseurl)
    print(driver.title)
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find('ul', {'id': "yema"})
    pages = ul.findAll('li')
    # get the last page
    lastpage = pages[-1]
    href = lastpage.find('a', href = True)
    url = href['href']
    # get total number of pages
    totalpages = int(url[-2:])
    print(totalpages)
    for i in range(totalpages):
        pageurl = url[:-2] + str(i + 1)
        print(pageurl)
        downloadPage(driver, pageurl)
        
    driver.quit()