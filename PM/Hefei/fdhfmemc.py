# -*- coding: utf-8 -*-
#===============================================================================
#               Fetch PM2.5,PM10,SO2,NO2,CO,1hO3,8hO3 data from 
#           http://218.23.98.205:8080/aqi/s/aqi/aqirtsumdata/*List
#
#                       Version: 1.3.2 (2014-01-04)
#                         Interpreter: Python 3.3
#                   Test platform: Linux, Mac OS 10.9.1
#
#                     Author: Tony Tsai, Ph.D. Student
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
        self.id = ''  # 台站编号
        self.name = ''  # 台站名称
        self.success = False  # 数据请求成功标志
        self.AQI = ''  # 空气质量（分）指数:(I)AQI
        self.level = ''  # 空气质量级别
        self.acquire = '' # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary

# 请求数据
def requestData(WRWType):
    url = 'http://218.23.98.205:8080/aqi/s/aqi/aqirtsumdata/' + WRWType + 'List'  
    hfmemc = urllib.request.urlopen(url)
    # status code: 200 OK
    while(hfmemc.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(hfmemc.getcode()))
        # request again after 5min
        time.sleep(5 * 60)
        hfmemc = urllib.request.urlopen(url)
    # 返回数据为json格式
    json_res = hfmemc.read().decode('utf-8')
    
    # convert json to python
    py_res = json.loads(json_res, encoding = 'utf-8')
    return py_res

# 保存信息
def writeData(outfile, dictData):
    if not os.path.exists(outfile):
        header = False
    else:
        header = True
    f = codecs.open(outfile, 'a', 'utf-8')
    dictWriter = csv.DictWriter(f, dictData.keys())
    # only write header when create a new csv
    if not header:
        dictWriter.writeheader()
    dictWriter.writerow(dictData)
    f.close()
    
if __name__ == '__main__':
#    StationNames = ['明珠广场', '长江中路', '董铺水库', '琥珀山庄', '三里街子站',
#                    '高新区子站', '庐阳区子站', '瑶海区子站', '包河区子站', 
#                    '滨湖新区子站']
    # 观测指标
    WRWTypes = collections.OrderedDict([('aqi','AQI'), ('pmTwo','PM2.5'), ('pmTen','PM10'), ('so','SO2'),
                ('no','NO2'), ('co','CO'), ('oOne','1hO3'), ('oEigh','8hO3')])
    
    homedir = os.getcwd()
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)
                
    for WRWType in WRWTypes.keys():
        outdir = homedir + '/' + WRWTypes[WRWType] + '/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
                            
        outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
        try:
            res = requestData(WRWType)
            while(not res['success']):
                # request again after 2min
                time.sleep(2 * 60)
                res = requestData(WRWType)
                    
            data = res['data']
            numStation = data['total']
            rows = data['rows']
            for i in range(numStation):
                st = station()
                st.id = rows[i]['Id']
                st.name = rows[i]['Index']
                st.success = res['success']
                if WRWType == 'aqi':
                    st.AQI = rows[i]['Aqi']
                else:
                    st.AQI = rows[i]['Iaqi']
                    st.level = rows[i]['Lv']
                st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', nowstrp)
                # 给字典添加键值
                st.dict['台站编号'] = st.id
                st.dict['台站名称'] = st.name
                st.dict['(I)AQI'] = st.AQI
                st.dict['Level'] = st.level
                if WRWType == 'aqi':
                    st.dict['首要污染物'] = rows[i]['Poll']
                elif WRWType == 'pmTwo' or WRWType == 'pmTen':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['Pmone']
                    st.dict['24小时均值(微克/立方米)'] = rows[i]['Pmtwo']
                elif WRWType == 'so':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['So']
                elif WRWType == 'no':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['Notwo']
                elif WRWType == 'co':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['Co']
                elif WRWType == 'oOne':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['One']
                elif WRWType == 'oEigh':
                    st.dict['实时浓度(微克/立方米)'] = rows[i]['Oba']
                st.dict['获取时间'] = st.acquire

                writeData(outfile, st.dict)
                    
                print(st.name, WRWTypes[WRWType], st.acquire)
                for key, value in st.dict.items():
                    print('%s: %s' % (key, value))
                          
        except Exception as e:
            error = now + '\r\n' + WRWTypes[WRWType] +'\r\n' + traceback.format_exc() + '\r\n'
            print(error)
            f = codecs.open('error.log', 'a', 'utf-8')
            f.writelines(error)
            f.close()