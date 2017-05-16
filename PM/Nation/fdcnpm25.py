# -*- coding: utf-8 -*-
#===============================================================================
#      Scrape environmental monitoring data from http://www.cnpm25.cn/
#
#                       Version: 1.0.3 (2014-01-14)
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
import urllib.request, os, codecs, traceback, csv, collections, re, random
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from time import sleep

# global variables
# cities without monitoring PM2.5
aqi_cities = []
# cities with monitoring PM2.5
pm25_cities = []

class city:
    def __init__(self):
        self.name_cn = '' # 中文城市名称
        self.name_en = '' # 西文城市名称
        self.url = '' # 数据链接

class station:
    def __init__(self):
        self.city = '' # 所在城市
        self.name = '' # 台站名称
        self.url = ''      # 数据链接
        self.time_point = ''  # 更新时间
        self.dict = collections.OrderedDict([('city', ''), ('station', ''), ('time_point', ''), 
                                             ('primary_pollutant', ''), ('quality', ''), 
                                             ('aqi', ''), ('co', ''), ('no2', ''), ('o3', ''), 
                                             ('pm10', ''), ('pm25', ''), ('so2', ''), 
                                             ('url', '')])

# 请求数据
def reqWeb(url):
    # url example: http://www.cnpm25.cn/
    # add User-Agent information in request headers to avoid urllib2.HTTPError: HTTP Error 403: Forbidden
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko)'}
    req = urllib.request.Request(url = url, headers = headers)
    cnpm25 = urllib.request.urlopen(req, timeout = 10)
    response = cnpm25.read().decode('utf-8')
    cnpm25.close()
    soup = BeautifulSoup(response)
    # list for storing all cities
    cities = []
    divs = soup.findAll('div', {'class': 'warp'})
    for div in divs:
        h1 = div.findAll('a', href = re.compile('city/'))
        for h2 in h1:
            h3 = h2.findAll('a', href = re.compile('city/'))
            ct = city()
            if len(h3) == 0:
                ct.name_cn = h2.get_text().strip()
                ct.name_en = re.split('\/|\.', h2['href'])[1]
                ct.url = url + h2['href']
            else:
                for h4 in h3:
                    ct.name_cn = h4.get_text().strip()
                    ct.name_en = re.split('\/|\.', h4['href'])[1]
                    ct.url = url + h4['href']
            cities.append(ct)
    return(cities)

def reqCity(ct):
    url = ct.url
    # city url example: http://www.cnpm25.cn/beijing.html
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko)'}
    req = urllib.request.Request(url = url, headers = headers)
    cnpm25 = urllib.request.urlopen(req, timeout = 10)
    response = cnpm25.read().decode('utf-8')
    cnpm25.close()
    soup = BeautifulSoup(response)
    table = soup.find('table', {'id': 'xiang1'})
    if table is None:
        aqi_cities.append(ct)
        return(None)
    else:
        pm25_cities.append(ct)
        stations = []
        rows = table.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            # skip header
            if len(cols) == 0:
                continue
            
            st = station()
            st.city = ct.name_cn
            st.dict['city'] = st.city
            for i in range(len(cols)):
                col = cols[i]
                if i == 0:
                    st.name = col.get_text().strip()
                    st.dict['station'] = st.name
                    href = col.find('a', href = True)
                    if href is not None:
                        st.url = url.replace('city/' + ct.name_en + '.html', href['href'][3:].strip())
                        st.dict['url'] = st.url
                        # get time_point
                        st.time_point = soup.find('span', {'style': 'font-size:12px; font-weight:normal; margin-left:50px;'}).get_text().strip()[-16:]
                        st.dict['time_point'] = st.time_point
                elif i == 1:
                    st.dict['aqi'] = col.get_text().strip()
                elif i == 2:
                    st.dict['quality'] = col('img')[0]['alt'].split('：')[1]
                elif i == 3:
                    st.dict['pm25'] = re.sub('μg/m³', '', col.get_text().strip())
                elif i == 4:
                    st.dict['pm10'] = re.sub('μg/m³', '', col.get_text().strip())
                elif i == 5:
                    st.dict['primary_pollutant'] = col.get_text().strip()
            stations.append(st)
        return(stations)

def reqStation(st):
    url = st.url
    if url:
        # station url example: http://www.cnpm25.cn/mon/beijing_1.html
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko)'}
        req = urllib.request.Request(url = url, headers = headers)
        cnpm25 = urllib.request.urlopen(req, timeout = 10)
        while(cnpm25.getcode() != 200):
            sleep(random.randrange(1, 5))
            cnpm25 = urllib.request.urlopen(req, timeout = 10)
        response = cnpm25.read().decode('utf-8')
        cnpm25.close()
        soup = BeautifulSoup(response)
        td = soup.find('td', {'width': '820', 'class': 'warp'})
        st.time_point = td.find('h2').get_text().strip()[-16:]
        st.dict['time_point'] = st.time_point
        tp = datetime.strptime(st.time_point, '%Y-%m-%d %H:00')
        script = td.find('script', {'type': 'text/javascript'}).get_text().strip()
        if st.name in ['美国大使馆', '美国领事馆']:
            # 美国大使馆只有AQI和PM2.5数据
            types = ['aqi', 'pm25']
        else:
            types = ['aqi', 'pm25', 'pm10', 'co', 'so2', 'no2', 'o3']
        for t in types:
            pattern = r"\"<set name='" + re.escape(tp.strftime('%d')) + "日" + \
            re.escape(tp.strftime('%H')) + r"时' value='((?:\d+)?(?:\d+\.\d+)?)'.+>\"\r\ncreateflash\(flashvalue, \"chartdiv\",\"" + \
            re.escape(t) + r"\"\);"
            m = re.findall(pattern, script)
            if m:
                st.dict[t] = m[0]
    return(st)
    
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
    outdir = homedir + '/cnpm25/' 
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    now = datetime.now()
#     print(now.ctime())
    # data time point
    tp = now - timedelta(hours = 1)
    outfile = outdir + tp.strftime('%Y%m%d') + '.csv'
    
    url = 'http://www.cnpm25.cn/'                           
    try:
        # 获取网页信息 
        cities = reqWeb(url)
        if(cities):
            for ct in cities:
                stations = reqCity(ct)
                if stations is not None:
                    # only deal with pm25_cities
                    for st in stations:
                        try:
                            newst = reqStation(st)
                            writeData(outfile, newst.dict)

#                             for key,value in list(newst.dict.items()):
#                                 print('%s: %s' % (key, value))
                        except urllib.error.HTTPError as e:
                            if e.code == 404:
                                writeData(outfile, st.dict)
                                
#                                 for key,value in list(st.dict.items()):
#                                     print('%s: %s' % (key, value))
                                continue
    except Exception as e:
        error = now.ctime() + '\r\n' + traceback.format_exc() + '\r\n'
        print(error)
        f = codecs.open('error.log', 'a', 'utf-8')
        f.writelines(error)
        f.close()