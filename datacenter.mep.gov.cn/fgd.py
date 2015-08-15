# -*- coding: utf-8 -*-
#===============================================================================
#    Automatically download data from data center of Ministry of Environmental
#             Protection of the People's Republic of China
#                 (http://datacenter.mep.gov.cn/)
#
#                       Version: 1.0.0 (2015-08-15)
#                         Interpreter: Python 3.4
#                      Test platform: Mac OS 10.10.4
#
#                    Author: Tony Tsai, Ph.D. Candidate
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#           (Center for Earth System Science, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os, csv

def extractRow(row):
    data = []
    cols = row.findAll("td")
    for col in cols:
        #  remove \n and &nbsp;
        text = col.getText().replace('\n', '').replace(u'\xa0', '')
        data.append(text)
    return data

def downloadTable(table):
    rows = table.findAll("tr")
    tableName = extractRow(rows[0])[0]
    print(tableName)
    tableHeader = extractRow(rows[1])
    outfile = os.path.join(homeDir, tableName + ".csv")
    print(outfile)
    isExisted = os.path.isfile(outfile)
    with open(outfile, 'a', newline='', encoding="utf8") as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        if not isExisted:
            spamwriter.writerow(tableHeader)
        for row in rows[2:]:
            tableData = extractRow(row)
            spamwriter.writerow(tableData)
    csvfile.close()


def downloadPage(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # find data table
    table = soup.find("table", {"style": "margin:20px auto 0px auto"})
    downloadTable(table)


if __name__ == '__main__':
    homeDir = os.getcwd()
    print(homeDir)
    # url for 全国燃煤机组脱硫设施清单
    # url = "http://datacenter.mep.gov.cn/main/template-view.action?templateId_=8ae5e4b7473ae3ea01479f4c72b400a3&dataSource="
    # url for 全国水泥熟料生产线脱硝设施清单
    # url = "http://datacenter.mep.gov.cn/main/template-view.action?templateId_=8ae5e4b747bdca650148116045700099&dataSource="
    # url for 国家重点监控企业名单
    url = "http://datacenter.mep.gov.cn/main/template-view.action?templateId_=40288098292043970129204f5c6e000a&dataSource="

    # 启动真正的浏览器，可能带来两个问题：一是需要的时间较长，二是UI自动化易受干扰、不够稳定
    driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs198/1.9.8/bin/phantomjs')
    driver.get(url)
    print(driver.title)

    # Don't use proxy, otherwise the website can't be accessed.
    print("=== page: 1 ===")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # find data table
    table = soup.find("table", {"style": "margin:20px auto 0px auto"})
    downloadTable(table)

    # page numbers
    pageInfo = soup.findAll("font", {"style": "font-weight:bold;color:#004e98"})
    pageNum = pageInfo[1].getText()
    print("Total pages: " + pageNum)
    pages = range(1, int(pageNum))
    for page in pages:
        driver.find_element_by_link_text("下一页").click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form#mainForm"))
        )
        print("=== page: " + str(page + 1) + " ===")
        downloadPage(driver)

    driver.quit()