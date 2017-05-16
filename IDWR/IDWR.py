# -*- coding: utf-8 -*-
#===============================================================================
#    Automatically Download IDWR Surveillance Data Table from National 
#                 Institute of Infectious Diseases (NIID), Japan 
#  (https://www.niid.go.jp/niid/en/survaillance-data-table-english.html)
#
#                       Version: 1.0.0 (2017-05-15)
#                        Interpreter: Python 3.6.1
#                      Test platform: Mac OS 10.12.4
#
#                    Author: Jun Cai, Ph.D. Candidate
#          (Department of Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                   Copyright: belongs to Prof.Xu's Lab
#          (Department of Earth System Science, Tsinghua University)
#===============================================================================
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, urlencode
import os, requests

def downloadTable(table):
    hrefs = table.findAll('a', href = True)
    for href in hrefs:
        if href is not None:
            csvurl = "https://www.niid.go.jp" + href['href']
            print(csvurl)
            # extract output file name 
            filepaths = urlparse(csvurl).path.split("/")
            outdir = os.path.join(filepaths[-3], filepaths[-2])
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            filename = filepaths[-1]
            outfile = os.path.join(outdir, filename)
            print(outfile)
            # download csv file
            response = requests.get(csvurl, stream = True)
            # write response to file
            with open(outfile, 'wb') as csvfile:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk: # filter out keep-alive new chunks
                        csvfile.write(chunk)
            csvfile.close()
            
def downloadPage(driver, url):
    driver.get(url)
    print(driver.title)
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # find data table
    table = soup.find("table", {"style": "width: 550px;"})
    downloadTable(table)
    return(soup)

if __name__ == '__main__':
    # url for IDWR Surveillance Data Table
    url = "https://www.niid.go.jp/niid/en/survaillance-data-table-english.html"
    
    # 启动真正的浏览器，可能带来两个问题：一是需要的时间较长，二是UI自动化易受干扰、不够稳定
    driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')
    # Don't use proxy, otherwise the website can't be accessed.
    print("=== page: 1 ===")
    soup = downloadPage(driver, url)
    
    # page numbers
    pageInfo = soup.findAll("p", {"class": "counter"})
    pageStrings = pageInfo[0].getText().strip().split(" ")
    currentPage = pageStrings[1]
    pageNum = pageStrings[3]
    print("Total pages: " + pageNum)
    pages = range(1, int(pageNum))
    for page in pages:
        params = urlencode({"start": str(page)})
        pageurl = url + '?' + params
        print("=== page: " + str(page + 1) + " ===")
        soup = downloadPage(driver, pageurl)
    
    driver.quit()