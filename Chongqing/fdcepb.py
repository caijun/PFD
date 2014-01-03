# -*- coding: utf-8 -*-
#===============================================================================
#               Fetch PM2.5,PM10,SO2,NO2,CO,1hO3,8hO3 data from 
#                   http://www.cepb.gov.cn/kq/?index=1#
#
#                       Version: 1.2.1 (2013-06-25)
#                         Interpreter: Python 3.3
#                     Test platform: Windows 7, Linux
#
#                     Author: Tony Tsai, Ph.D. Student
#          (Center for Earth System Science, Tsinghua University)
#              Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
import urllib.request, urllib.error, os, time, traceback, codecs, json, collections, csv

class station:
    def __init__(self):
        self.id = ''  # 台站编号
        self.name = ''  # 台站名称
        self.dt = ''  # 发布时间
        self.acquire = '' # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary

# 请求数据
def requestData(payload):
    # HTTP POST request using json
    url = 'http://www.cepb.gov.cn/kq/Ajax.aspx/GetJCDList'
    headers = {'content-type': 'application/json'}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req)
        # Status code: 200 OK
    except urllib.error.HTTPError as e:
        print('Server connection error, status code:', e.code)
        # request again after 5min
        time.sleep(5 * 60)
        response = urllib.request.urlopen(req)
    # 返回数据为json格式
    json_res = response.read().decode('utf-8')
    
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
    StationNames = ['解放碑', '潘家坪', '新山村', '唐家沱', '高家花园',
                    '花溪', '杨家坪', '白市驿', '南坪', '茶园', '天生', 
                    '缙云山', '蔡家', '两路', '空港', '鱼新街', 
                    '南泉', '礼嘉']
    # 观测指标
    WRWTypes = collections.OrderedDict([('PM21','PM2.5'), ('PM101','PM10'), ('SO21','SO2'),
                ('NO21','NO2'), ('CO1','CO'), ('O31','O3')])
    
    homedir = os.getcwd()
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)
    
    for i in range(len(StationNames)):
        payload = {'id': str(i)}
                
        try:
            # 返回数据类型string
            res = requestData(payload)
            # 去掉首尾[],并转换为dict
            data = eval(res[1:-1])
            
            st = station()
            st.id = data['SITE_CODE1']
            st.name = data['SITE_NAME1']
            strDateTime = data['MONITOR_DATE1']
            DateTime = time.strptime(strDateTime, '%Y年%m月%d日 %H时')
            st.dt = time.strftime('%Y-%m-%d %H:%M:%S', DateTime)
            st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime()))
            
            for WRWType in WRWTypes.keys():
                st.dict['台站编号'] = st.id
                st.dict['台站名称'] = st.name
                st.dict['发布时间'] = st.dt
                # 去掉末尾的单位u g/m3,注意u占1个字符
                st.dict['实时浓度(微克/立方米)'] = data[WRWType][:-5]
                st.dict['获取时间'] = st.acquire
                
                outdir = homedir + '/' + WRWTypes[WRWType] + '/'
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                            
                outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
                writeData(outfile, st.dict)
                
                print(st.name, WRWTypes[WRWType], st.dt)
                for key, value in st.dict.items():
                    print('%s: %s' % (key, value))
                    
        except Exception as e:
            error = now + '\r\n' + StationNames[i] +'\r\n' + \
            traceback.format_exc() + '\r\n'
            print(error)
            f = codecs.open('error.log', 'a', 'utf-8')
            f.writelines(error)
            f.close()