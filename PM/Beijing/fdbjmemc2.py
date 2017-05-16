# -*- coding: utf-8 -*-
#===============================================================================
#      Scrape PM2.5,PM10,SO2,NO2,CO,O3 data From http://zx.bjmemc.com.cn/
#
#                       Version: 1.4.3 (2014-01-04)
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
import urllib.request, urllib.parse, os, time, codecs, traceback, csv, collections, json

class station:
    def __init__(self):
        self.name = ''  # 台站名称
        self.WRWType = ''  # 污染物类型
        self.GB24h = ''  # 24小时浓度国标
        self.avg24h = '' # 24小时平均浓度
        self.unit = ''  # 单位
        self.dt = ''  # 发布日期时间
        self.acquire = '' # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary, key and value

# 请求数据
def requestData(StationName, WRWType):
    # http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetChartData_ByStationAndWRWType&StationName=奥体中心&WRWType=PM2.5
    url = 'http://zx.bjmemc.com.cn/ashx/Data.ashx'
    values = {'Action':'GetChartData_ByStationAndWRWType',
              'StationName':StationName,
              'WRWType':WRWType}
    data = urllib.parse.urlencode(values)
    bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # status code: 200 OK
    while(bjmemc.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(bjmemc.getcode()))
        # request again after 5min
        time.sleep(5 * 60)
        bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # 返回数据为json格式
    json_res = bjmemc.read().decode('utf-8')
    
    # convert json to python
    py_res = json.loads(json_res, encoding = 'utf-8')
    return py_res
    
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
#     StationNames = ['奥体中心']
    StationNames = ['奥体中心', '八达岭', '北部新区', '昌平', '大兴',
                   '定陵', '东高村', '东四', '东四环', '房山',
                   '丰台花园', '古城', '官园', '怀柔', '琉璃河',
                   '门头沟', '密云', '密云水库', '南三环', '农展馆',
                   '平谷', '前门', '顺义', '天坛', '通州',
                   '万柳', '万寿西宫', '西直门北', '延庆', '亦庄',
                   '永定门内', '永乐店', '榆垡', '云岗', '植物园']
#     WRWTypes = ['NO2']
    WRWTypes = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    homedir = os.getcwd()
    
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)
        
    for WRWType in WRWTypes:
        outdir = homedir + '/' + WRWType + '/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)       
        outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
        
        for StationName in StationNames:
            st = station()         
            try:
                res = requestData(StationName, WRWType)
                if(res):
                    print(res)
                    st.name = res['StationName']
                    st.WRWType = res['WRWName']
                    st.GB24h = res['GB24h']
                    st.avg24h = res['Avg24h']
                    st.unit = res['Units']
                    st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime()))
                    # 过去24个小时浓度
                    data = res['Datas']
                    for item in data:
                        st.dict['台站'] = st.name
                        st.dt = item['DTime']
                        st.dict['发布时间'] = st.dt
                        st.dict['实时浓度(' + st.unit + ')'] = item['Value']
                        st.dict['获取时间'] = st.acquire
                    
                        writeData(outfile, st.dict)
                        for key, value in list(st.dict.items()):
                            print(('%s: %s' % (key, value)))                                                              
                        
            except Exception as e:
                error = now + '\r\n' + WRWType + ',' + StationName + '\r\n' + traceback.format_exc() + '\r\n'
                print(error)
                f = codecs.open('error.log', 'a', 'utf-8')
                f.writelines(error)
                f.close()