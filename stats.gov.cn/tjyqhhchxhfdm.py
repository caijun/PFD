# -*- coding: utf-8 -*-
#===============================================================================
#      Fetch statistical and rural division code from http://www.stats.gov.cn/
#
#                       Version: 1.0.0 (2014-03-05)
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
import urllib.request, urllib.error, csv, os, codecs, http.client

province = {'北京': '北京市', '天津': '天津市', '河北': '河北省', '山西': '山西省', '内蒙古': '内蒙古自治区', 
            '辽宁': '辽宁省', '吉林': '吉林省', '黑龙江': '黑龙江省', '上海': '上海市', '江苏': '江苏省', 
            '浙江': '浙江省', '安徽': '安徽省', '福建': '福建省', '江西': '江西省', '山东': '山东省', 
            '河南': '河南省', '湖北': '湖北省', '湖南': '湖南省', '广东': '广东省', '广西': '广西壮族自治区', 
            '海南': '海南省', '重庆': '重庆市', '四川': '四川省', '贵州': '贵州省', '云南': '云南省', 
            '西藏': '西藏自治区', '陕西': '陕西省', '甘肃': '甘肃省', '青海': '青海省', '宁夏': '宁夏回族自治区', 
            '新疆': '新疆维吾尔自治区', '台湾': '台湾省', '香港': '香港特别行政区', '澳门': '澳门特别行政区'}
# format:{code1: name1, code2: name2}
province_dict = {}
city_dict = {}
county_dict = {}
town_dict = {}
village_dict = {}


# administrative region
class admin():
    def __init__(self, level):
        self.code = '' # 代码
        self.name = '' # 名称
        self.level = level # 行政区级别
        self.address = '' # 地址
        if level == 'village':
            self.category = '' # 城乡分类
        else:
            self.url = '' # url链接
    
    def __str__(self):
        l = []
        for key in self.__dict__:
            l.append("{key}='{value}'".format(key = key, value = self.__dict__[key]))
        return ', '.join(l)
    
    def __repr__(self):
        return self.__str__()    

# request province|city|county|town
def reqData(url, level):
    code = url.split('/')[-1].replace('.html', '')
    
    req = urllib.request.urlopen(url)
    res = req.read().decode('gb18030')
    soup = BeautifulSoup(res)
    table = soup.find('table', {'class': level + 'table'})
    head = table.find('tr', {'class': level + 'head'}).get_text(" ").strip()
    # print(head)
    if level == 'province':
        note = table.find('td', {'colspan': '8', 'height': '50'}).get_text().strip()
        print(note)
    # administrative regions
    ars = []
    trs = table.findAll('tr', {'class': level + 'tr'})
    for tr in trs:
        tds = tr.findAll('td')
        if level == 'province':
            for td in tds:
                href = td.find('a', href = True)
                if href is not None:
                    ar = admin(level)
                    if href.get_text().strip() in province:
                        ar.name = province[href.get_text().strip()]
                    else:
                        ar.name = href.get_text().strip()
                    ar.url = url.replace('index.html', href['href'])
                    ar.code = href['href'].replace('.html', '')
                    if ar.name in ['北京', '北京市', '天津', '天津市', '上海', '上海市', '重庆', '重庆市']:
                        ar.level = 'municipality'
                    ar.address = ar.name
                    province_dict[ar.code] = ar.address
                    ars.append(ar)
        elif level == 'city':
            td = tds[-1]
            href = td.find('a', href = True)
            if href is not None:
                ar = admin(level)
                ar.name = href.get_text().strip()
                codes = href['href'].replace('.html', '').split('/')
                citycode = codes[-1]
                ar.url = url.replace(code + '.html', href['href'])
                ar.code = citycode
                if ar.name in ['市辖区', '县', '省直辖县级行政区划', '自治区直辖县级行政区划']:
                    ar.address = province_dict[code]
                else:
                    ar.address = province_dict[code] + ar.name
                city_dict[ar.code] = ar.address
                ars.append(ar)
        elif level == 'county':
            td = tds[-1]
            ar = admin(level)
            href = td.find('a', href = True)
            if href is not None:
                ar.name = href.get_text().strip()
                codes = href['href'].replace('.html', '').split('/')
                countycode = codes[-1]
                ar.url = url.replace(code + '.html', href['href'])
            else:
                ar.name = tds[1].get_text().strip()
                countycode = tds[0].get_text().strip()[0:6]
                ar.url = url.replace(code + '.html', 
                                     countycode[2:4] + '/' + countycode + '.html')
                ar.level = 'municipal district'
            ar.code = countycode
            ar.address = city_dict[code] + ar.name
            county_dict[ar.code] = ar.address
            ars.append(ar)
        elif level == 'town':
            td = tds[-1]
            href = td.find('a', href = True)
            if href is not None:
                ar = admin(level)
                ar.name = href.get_text().strip()
                codes = href['href'].replace('.html', '').split('/')
                towncode = codes[-1]
                ar.url = url.replace(code + '.html', href['href'])
                ar.code = towncode
                if '办事处' in ar.name:
                    if code not in ['4419', '4420']:
                        ar.address = county_dict[code] + ar.name.replace('办事处', '')
                    else:
                        ar.address = city_dict[code] + ar.name.replace('办事处', '')
                else:
                    if code not in ['4419', '4420']:
                        ar.address = county_dict[code] + ar.name
                    else:
                        ar.address = city_dict[code] + ar.name
                town_dict[ar.code] = ar.address
                ars.append(ar)
        elif level == 'village':
            ar = admin(level)
            ar.code = tds[0].get_text().strip()
            ar.category = tds[1].get_text().strip()
            ar.name = tds[2].get_text().strip()
            if '居民委员会' in ar.name:
                ar.address = town_dict[code] + ar.name.replace('居民委员会', '')
            elif '居委会' in ar.name:
                ar.address = town_dict[code] + ar.name.replace('居委会', '')
            elif '村民委员会' in ar.name:
                ar.address = town_dict[code] + ar.name.replace('村民委员会', '')
            elif '村委会' in ar.name:
                ar.address = town_dict[code] + ar.name.replace('村委会', '')
            else:
                ar.address = town_dict[code] + ar.name
            village_dict[ar.code] = ar.address
            ars.append(ar)
    return(ars)

# write data to csv file
def writeData(outfile, dictData):
    if not os.path.exists(outfile):
        header = False
    else:
        header = True
    f = codecs.open(outfile, 'a', 'gb18030')
    keys = []
    values = []
    for k in dictData.keys():
        keys.append(k)
        values.append(dictData[k])
    spamwriter = csv.writer(f)
    # only write header when create a new csv
    if not header:
        spamwriter.writerow(keys)
    spamwriter.writerow(values)
    f.close()

if __name__ == '__main__':
    homedir = os.getcwd() 
    
    url = 'http://www.stats.gov.cn'
    srdc_url = url + '/tjsj/tjbz/tjyqhdmhcxhfdm/'
    print(srdc_url)
    srdc = urllib.request.urlopen(srdc_url)
    srdc_res = srdc.read().decode('utf-8')
    srdc_soup = BeautifulSoup(srdc_res)
    list = srdc_soup.find('ul', {'class': 'center_list_contlist'})
    hrefs = list.findAll('a', href = True)
    if hrefs is not None:
        for href in hrefs:
            year = href['href'].split('/')[-2]
            if year in ['2013']:
                continue
            
            year_url = url + href['href']
            print(year_url)
            outdir = homedir + '/' + year + '/'
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            
            pros = reqData(year_url, 'province')
            province_file = outdir + 'province.csv'
            for p in pros:
                print(p.__dict__)
                writeData(province_file, p.__dict__)
                
                try:
                    cities = reqData(p.url, 'city')
                except http.client.BadStatusLine as e:
                    print(e)
                    cities = reqData(p.url, 'city') 
                city_file = outdir + 'city.csv'
                for c in cities:
                    print(c.__dict__)
                    writeData(city_file, c.__dict__)
                    
                    # 注意东莞市和中山市不设县
                    if c.code in ['4419', '4420']:
                        try:
                            towns = reqData(c.url, 'town')
                        except http.client.BadStatusLine as e:
                            print(e)
                            towns = reqData(c.url, 'town')
                        town_file = outdir + 'town.csv'
                        for t in towns:
                            print(t.__dict__)
                            writeData(town_file, t.__dict__)
                            
                            try:                            
                                villages = reqData(t.url, 'village')
                            except http.client.BadStatusLine as e:
                                print(e)
                                villages = reqData(t.url, 'village')
                            village_file = outdir + 'village.csv'
                            for v in villages:
                                print(v.__dict__)
                                writeData(village_file, v.__dict__)
                    else:
                        try:
                            counties = reqData(c.url, 'county')
                        except http.client.BadStatusLine as e:
                            print(e)
                            counties = reqData(c.url, 'county')
                        county_file = outdir + 'county.csv'
                        for ct in counties:
                            print(ct.__dict__)
                            writeData(county_file, ct.__dict__)
                            
                            try:
                                towns = reqData(ct.url, 'town')
                            except urllib.error.HTTPError as e:
                                if e.code == 404:
                                    print(e.code)
                                    continue
                            except http.client.BadStatusLine as e:
                                print(e)
                                towns = reqData(ct.url, 'town')
                            town_file = outdir + 'town.csv'
                            for t in towns:
                                print(t.__dict__)
                                writeData(town_file, t.__dict__)
                            
                                try:                            
                                    villages = reqData(t.url, 'village')
                                except urllib.error.HTTPError as e:
                                    if e.code == 404:
                                        print(e.code)
                                        continue
                                except http.client.BadStatusLine as e:
                                    print(e)
                                    villages = reqData(t.url, 'village')
                                village_file = outdir + 'village.csv'
                                for v in villages:
                                    print(v.__dict__)
                                    writeData(village_file, v.__dict__)