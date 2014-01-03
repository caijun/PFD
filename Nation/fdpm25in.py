# -*- coding: utf-8 -*-
#===============================================================================
#      Scrape environmental monitoring data from http://cdc.bjmb.gov.cn/
#
#                       Version: 1.0.0 (2014-01-04)
#                         Interpreter: Python 3.3
#                   Test platform: Linux, Mac OS 10.9.1
#
#                    Author: Tony Tsai, Ph.D. Student
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
import urllib.request, os, time, codecs, traceback, csv, collections, re
from bs4 import BeautifulSoup

class city:
    def __init__(self):
        self.name_cn = ''  # 中文城市名
        self.name_en = ''  # 西文城市名
        self.url = ''      # 数据链接
        self.acquire = ''  # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary, key and value

# 请求数据
def requestData(url):
    # url example: http://www.pm25.in/anshan
    pm25in = urllib.request.urlopen(url)
    # status code: 200 OK
    while(pm25in.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(pm25in.getcode()))
        # request again after 5s
        time.sleep(5)
        pm25in = urllib.request.urlopen(url)
    # urlopen() returns a bytes object
    response = pm25in.read().decode('utf-8')
    soup = BeautifulSoup(response)
    # find data table
    table = soup.find('table', {'id':'detail-data'})
    rows = table.findAll('tr')
    # store all of the records
    records = []
    for row in rows:
        cols = row.findAll('td')
        if len(cols) == 0:
            cols = row.findAll('th')
        record = []
        for col in cols:
            record.append(re.sub('\s+', ' ', col.get_text()))
        records.append(record)
    return(records)
    
# 保存信息
def writeData(outfile, dictData):
    if not os.path.exists(outfile):
        header = False
    else:
        header = True
    f = codecs.open(outfile, 'a', 'gbk')
    dictWriter = csv.DictWriter(f, list(dictData.keys()))
    # only write header when create a new csv
    if not header:
        dictWriter.writeheader()
    dictWriter.writerow(dictData)
    f.close()

if __name__ == '__main__':
    homedir = os.getcwd()
    outdir = homedir + '/pm25in/' 
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)       
    outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
    
    url = 'http://www.pm25.in'
    pm25in = urllib.request.urlopen(url)
    response = pm25in.read().decode('utf-8')
    soup = BeautifulSoup(response)
    divs = soup.findAll('div', {'class': 'all'})
    for div in divs:
        hrefs = div.findAll('a', href = True)
        for href in hrefs:
            ct = city()
            ct.name_cn = href.get_text()
            ct.name_en = href['href'][1:]
            ct.url = url + href['href']
                           
            try:
                # 获取网页信息
                table = requestData(ct.url)
                if(table):
                    ct.acquire = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime()))
                    header = table[0]
                    data = table[1:]
                    # add key, value to city.dict
                    for row in data:
                        ct.dict['城市中文名'] = ct.name_cn
                        ct.dict['城市西文名'] = ct.name_en
                        for col in header:
                            ct.dict[col] = row[header.index(col)]
                        ct.dict['链接'] = ct.url
                        ct.dict['获取时间'] = ct.acquire
                        
                        writeData(outfile, ct.dict)
                        
                        for key, value in list(ct.dict.items()):
                            print(('%s: %s' % (key, value)))
            except Exception as e:
                error = now + '\r\n' + ct.name_cn + '\r\n' + traceback.format_exc() + '\r\n'
                print(error)
                f = codecs.open('error.log', 'a', 'utf-8')
                f.writelines(error)
                f.close()