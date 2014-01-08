# -*- coding: utf-8 -*-
#===============================================================================
#     Scrape environmental monitoring data through json API provided by 
#                           http://www.pm25.in/
#
#                       Version: 1.0.0 (2014-01-08)
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
import urllib.request, os, time, codecs, traceback, csv, collections, json

class station:
    def __init__(self):
        self.area = '' # 城市名称
        self.position_name = '' # 监测点名称
        self.station_code = '' # 监测点编码
        self.time_point = '' # 数据发布时间
        # ordered dictionary, key and value
        # primary_pollutant: 首要污染物
        # quality: 空气质量指数类别,有“优、良、轻度污染、中度污染、重度污染、严重污染”6类
        # aqi:空气质量指数(AQI),即Air Quality Index,是定量描述空气质量状况的无量纲指数
        # co: 一氧化碳1小时平均
        # co_24h: 一氧化碳24小时平均
        # no2: 二氧化氮1小时平均
        # no2_24h: 二氧化氮24小时滑动平均
        # o3: 臭氧1小时平均
        # o3_24h: 臭氧日最大1小时平均
        # o3_8h: 臭氧8小时滑动平均
        # o3_8h_24h: 臭氧日最大8小时滑动平均
        # pm10: 颗粒物(粒径小于等于10um)1小时平均
        # pm10_24h: 颗粒物(粒径小于等于10um)24小时滑动平均
        # pm2_5: 颗粒物(粒径小于等于2.5um)1小时平均
        # pm2_5_24h: 颗粒物(粒径小于等于2.5um)24小时滑动平均
        # so2: 二氧化硫1小时平均
        # so2_24h: 二氧化硫24小时滑动平均
        self.dict = collections.OrderedDict([('area', ''), ('position_name', ''), ('station_code', ''), 
                                             ('time_point', ''), ('primary_pollutant', ''), ('quality', ''),  
                                             ('aqi', ''), ('co', ''), ('co_24h', ''), ('no2', ''), 
                                             ('no2_24h', ''), ('o3', ''), ('o3_24h', ''), ('o3_8h', ''), 
                                             ('o3_8h_24h', ''), ('pm10', ''), ('pm10_24h', ''), ('pm2_5', ''), 
                                             ('pm2_5_24h', ''), ('so2', ''), ('so2_24h', '')])

# 请求数据
def requestData(url):
    pm25in = urllib.request.urlopen(url)
    # 返回数据为json格式
    json_file = pm25in.read().decode('utf-8')
    # convert json to python
    json_data = json.loads(json_file, encoding = 'utf-8')
    return json_data
    
    
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
    
    outdir = homedir + '/all_cities/' 
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    now = time.ctime()
#     print(now)
    nowstrp = time.strptime(now)       
    outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
    
    url = 'http://www.pm25.in/api/querys/all_cities.json?token=heUpypsDpGnvKduwnmPV'           
    try:
        # 获取网页信息
        data = requestData(url)
        if(data):
            if len(data) == 1:
                error = now + '\r\n' + data['error'] + '\r\n'
                print(error)
            else:
                for position in data:
                    st = station()
                    for key in st.dict.keys():
                        st.dict[key] = position[key]
                    st.area = position['area']
                    st.position_name = position['position_name']
                    st.station_code = position['station_code']
                    st.time_point = position['time_point']
                    
                    writeData(outfile, st.dict)
                    
#                     for key, value in list(st.dict.items()):
#                         print(('%s: %s' % (key, value)))
                             
    except Exception as e:
        error = now + '\r\n' + traceback.format_exc() + '\r\n'
        print(error)
        f = codecs.open('error.log', 'a', 'utf-8')
        f.writelines(error)
        f.close()