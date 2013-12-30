# -*- coding: utf-8 -*-
#===============================================================================
#      Fetch PM2.5,PM10,SO2,NO2,CO,O3 Data From http://zx.bjmemc.com.cn/
#
#                       Version: 1.3.3 (2013-06-30)
#                         Interpreter: Python 3.3
#                     Test platform: Windows 7, Linux
#
#        Author: Tony Tsai, Ph.D. Student (with help from Cokefish)
#          (Center for Earth System Science, Tsinghua University)
#                   Contact Email: tony.tsai@whu.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
# TODO: 代码优化，提高访问成功率，降低访问次数
# 将每天每个台站一个文件改成每天一个文件，过多小文件便于拷贝，降低效率。
import urllib.request, urllib.parse, os, time, codecs, traceback, csv, collections
import xml.dom.minidom

class station:
    def __init__(self):
        self.name = ''  # 台站名称
        self.type = ''  # 台站类型
        self.WRWType = ''  # 污染物类型
        self.date = ''  # 发布日期
        self.time = ''  # 发布时间
        self.acquire = '' # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary, key and value

# 请求数据
def requestData(StationName, WRWType):
    # http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetWRWInfo_ByStationAndWRWType&StationName=奥体中心&WRWType=PM2.5
    # 地址
    url = 'http://zx.bjmemc.com.cn/ashx/Data.ashx?GetWRWInfo_ByStationAndWRWType'

    values = {'StationName':StationName, 
            'WRWType':WRWType}
    data = urllib.parse.urlencode(values)
    bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # Status code: 200 OK
    while(bjmemc.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(bjmemc.getcode()))
        # request again after 10min
        time.sleep(10*60)
        bjmemc = urllib.request.urlopen("%s?%s" % (url, data))
    # urlopen() returns a bytes object
    response = bjmemc.read().decode('utf-8')
    response = response.replace('<br>', '')
    # 去掉次一级<span><\span>
    response = response.replace(('<span id=\"StationTypeSpan\" style=\'font-family: arial, sans-serif;'
                                 'font-size: 15px;font-weight: bold;letter-spacing: -0.4pt;word-spacing: 0pt;'
                                 'line-height: 1.8;\'>(环境评价点)</span>&nbsp;'), ' (环境评价点)')
    response = response.replace('&nbsp;', ' ')
#    print response

    dom = xml.dom.minidom.parseString(response)
    root = dom.documentElement
    divs = root.getElementsByTagName('div')
    for div in divs:
        if div.getAttribute('id') == 'wrwqp_2':
            return div
    
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
#    StationNames = ['植物园']
    StationNames = ['奥体中心', '八达岭', '北部新区', '昌平', '大兴',
                   '定陵', '东高村', '东四', '东四环', '房山',
                   '丰台花园', '古城', '官园', '怀柔', '琉璃河',
                   '门头沟', '密云', '密云水库', '南三环', '农展馆',
                   '平谷', '前门', '顺义', '天坛', '通州',
                   '万柳', '万寿西宫', '西直门北', '延庆', '亦庄',
                   '永定门内', '永乐店', '榆垡', '云岗', '植物园']
    WRWTypes = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    homedir = os.getcwd()
    # 创建一个矩阵记录上次成功获取数据的小时,初始值为''
    lastHour = [['' for col in range(len(WRWTypes))] \
                for row in range(len(StationNames))]
    
    while(True):
        now = time.ctime()
        print(now)
        nowstrp = time.strptime(now)
        curHour = time.strftime('%H', nowstrp)
        
        for WRWType in WRWTypes:
            for StationName in StationNames:
                if curHour != lastHour[StationNames.index(StationName)][WRWTypes.index(WRWType)]:
                    st = station()
                    temp = []
                    # os.altsep is set to '/' on Windows systems where sep is a backslash
                    outdir = (homedir + '/' + WRWType + '/' + StationName + '/').encode('gbk')
                    if not os.path.exists(outdir):
                        os.makedirs(outdir)
                        
                    try:
                        # 获取页面信息
                        data = requestData(StationName, WRWType)
                        if(data):
                            divs = data.getElementsByTagName('div')
                            for div in divs:
                                spans = div.getElementsByTagName('span')
                                for span in spans:
#                                   print span.childNodes[0].data.strip()
                                    temp.append(span.childNodes[0].data.strip())
                            # 站点基本信息
                            info = temp[3].split(' ') 
                            st.name = info[0]
                            # 去掉首尾圆括号
                            st.type = info[1][1:-1]
                            st.WRWType = info[2]
                            # O3不返回发布日期和发布时间信息
                            if WRWType != 'O3': 
                                st.date = info[3]
                                st.time = info[4]
                            else:
                                st.date = time.strftime('%Y-%m-%d', nowstrp)
                                st.time = curHour + ':00:00'
                            st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', nowstrp)
                            # 给字典添加键值
                            st.dict['Time'] = st.time
                            # 污染物观测指标和观测值
                            st.dict[temp[0] + temp[1]] = temp[2]
                            st.dict[temp[4] + temp[5]] = temp[6]
                            st.dict[temp[7] + temp[8]] = temp[9]
                            st.dict[temp[10]] = temp[11] + ' ' + temp[12]
                            st.dict['获取时间'] = st.acquire
                
                            outfile = (outdir.decode('gbk') + time.strftime('%Y%m%d', nowstrp) + '.csv').encode('gbk')
                            print(outfile.decode('gbk'))
                            writeData(outfile, st.dict)
                            # Update lastHour
                            lastHour[StationNames.index(StationName)][WRWTypes.index(WRWType)] = curHour
                
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
        # 休眠15*60s, 每15min发送一次请求
        time.sleep(15*60)
