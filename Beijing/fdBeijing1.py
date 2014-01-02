# -*- coding: utf-8 -*-
#===============================================================================
#      Fetch PM2.5,PM10,SO2,NO2,CO,O3 data from http://zx.bjmemc.com.cn/
#
#                       Version: 1.5.4 (2014-01-02)
#                         Interpreter: Python 3.3
#                   Test platform: Linux, Mac OS 10.9.1
#
#        Author: Tony Tsai, Ph.D. Student (with help from Cokefish)
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
import urllib.request, urllib.parse, os, time, codecs, traceback, csv, collections
from bs4 import BeautifulSoup

class station:
    def __init__(self):
        self.name = ''  # 台站名称
        self.type = ''  # 台站类型
        self.WRWType = ''  # 污染物类型
        self.date = ''  # 发布日期
        self.time = ''  # 发布时间
        self.acquire = ''  # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary, key and value

# 请求数据
def requestData(StationName, WRWType):
    # http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetWRWInfo_ByStationAndWRWType&StationName=奥体中心&WRWType=PM2.5
    url = 'http://zx.bjmemc.com.cn/ashx/Data.ashx'
    Action = 'GetWRWInfo_ByStationAndWRWType'
    values = {'Action':Action,
              'StationName':StationName,
              'WRWType':WRWType}
    data = urllib.parse.urlencode(values)
    bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # Status code: 200 OK
    while(bjmemc.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(bjmemc.getcode()))
        # request again after 10min
        time.sleep(10 * 60)
        bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # urlopen() returns a bytes object
    response = bjmemc.read().decode('utf-8')
    soup = BeautifulSoup(response)
    fd = []
    for string in soup.stripped_strings:
        fd.append(string)
    return(fd)
    
# 保存信息
def writeData(outfile, dictData):
    if not os.path.exists(outfile):
        header = False
    else:
        header = True
    f = codecs.open(outfile, 'a', 'gbk')
    dictWriter = csv.DictWriter(f, list(dictData.keys()))
    # Only write header when create a new csv
    if not header:
        dictWriter.writeheader()
    dictWriter.writerow(dictData)
    f.close()

if __name__ == '__main__':
#     StationNames = ['植物园']
    StationNames = ['奥体中心', '八达岭', '北部新区', '昌平', '大兴',
                   '定陵', '东高村', '东四', '东四环', '房山',
                   '丰台花园', '古城', '官园', '怀柔', '琉璃河',
                   '门头沟', '密云', '密云水库', '南三环', '农展馆',
                   '平谷', '前门', '顺义', '天坛', '通州',
                   '万柳', '万寿西宫', '西直门北', '延庆', '亦庄',
                   '永定门内', '永乐店', '榆垡', '云岗', '植物园']
#     WRWTypes = ['PM2.5']
    WRWTypes = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    homedir = os.getcwd()
    
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)
        
    for WRWType in WRWTypes:
        # os.altsep is set to '/' on Windows systems where sep is a backslash
        outdir = homedir + '/' + WRWType + '/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)       
        outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
                
        for StationName in StationNames:
            st = station()                        
            try:
                # 获取网页信息
                data = requestData(StationName, WRWType)
                if(data):
                    # 站点基本信息
                    st.name = data[3]
                    # Remove parentheses
                    st.type = data[4][1:-1]
                    # \xa0 is unicode for NO-BREAK SPACE
                    rs = data[5].replace('\N{NO-BREAK SPACE}', ' ').split(' ')
                    st.WRWType = rs[0]
                    # O3不返回发布日期和发布时间信息
                    if WRWType != 'O3': 
                        st.date = rs[1]
                        st.time = rs[2]
                    else:
                        st.date = time.strftime('%Y-%m-%d', nowstrp)
                        st.time = time.strftime('%H', nowstrp) + ':00:00'
                    st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', nowstrp)
                    # 给字典添加键值
                    st.dict['Time'] = st.time
                    st.dict['Station'] = st.name
                    # 污染物观测指标和观测值
                    st.dict[data[0] + data[1]] = data[2]
                    st.dict[data[6] + data[7]] = data[8]
                    st.dict[data[9] + data[10]] = data[11]
                    st.dict[data[12]] = data[13] + ' ' + data[14]
                    st.dict['获取时间'] = st.acquire
                
                    writeData(outfile, st.dict)
                
                    print(st.name, st.type, st.WRWType, st.date, st.time)
                    for key, value in list(st.dict.items()):
                        print(('%s: %s' % (key, value)))
            except Exception as e:
                error = now + '\r\n' + WRWType + ',' + StationName + '\r\n' + \
                traceback.format_exc() + '\r\n'
                print(error)
                f = codecs.open('error.log', 'a', 'utf-8')
                f.writelines(error)
                f.close()