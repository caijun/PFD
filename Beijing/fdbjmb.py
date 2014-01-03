# -*- coding: utf-8 -*-
#===============================================================================
#         Fetch meteorological data from http://cdc.bjmb.gov.cn/
#
#                       Version: 1.0.0 (2014-01-02)
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
import urllib.request, urllib.parse, os, time, codecs, traceback, csv, collections
from bs4 import BeautifulSoup

class station:
    def __init__(self):
        self.name = ''  # 台站名称
        self.acquire = ''  # 获取时间
        self.dict = collections.OrderedDict()  # ordered dictionary, key and value

# 请求数据
def requestData(id):
    # http://cdc.bjmb.gov.cn/gongzhong.asp?id=0
    url = 'http://cdc.bjmb.gov.cn/gongzhong.asp'
    values = {'id':id}
    data = urllib.parse.urlencode(values)
    bjmb = urllib.request.urlopen("%s?%s" % (url, data))
    # status code: 200 OK
    while(bjmb.getcode() != 200):
        raise Exception('Server connection error, status code:' + str(bjmb.getcode()))
        # request again after 5min
        time.sleep(5 * 60)
        bjmb = urllib.request.urlopen("%s?%s" % (url, data))
    # urlopen() returns a bytes object
    response = bjmb.read().decode('gbk')
    soup = BeautifulSoup(response)
    # find data table
    table = soup.find('table', {'width':567})
    rows = table.findAll('tr')
    # store all of the records
    records = []
    for row in rows:
        cols = row.findAll('td')
        record = []
        for col in cols:
            record.append(col.get_text())
        records.append(record)
    # deal with table header
    a = records[0]
    a.insert(6, a[5])
    a.insert(8, a[7])
    b = records[1]
    b = ['', '', '', '', ''] + b
    # remove 1st and 2nd elements from records
    del records[0:2]
    records.insert(0, [x + y for x, y in zip(a, b)])
    return(records)
    
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
#     stations = {'观象台':0}
    stations = collections.OrderedDict([('观象台', 0), ('海淀', 1), ('朝阳', 2), ('石景山', 3), ('丰台', 4), ('天安门', 5), ('官园', 6), 
                                        ('四元桥', 7), ('紫竹院', 8), ('大观园', 9), ('天坛', 10), ('世界公园', 11), ('八大处', 12), 
                                        ('顺义', 13), ('延庆', 14), ('密云', 15), ('怀柔', 16), ('昌平', 17), ('门头沟', 18), ('房山', 19), 
                                        ('妙峰山', 20), ('金海湖', 21), ('工人体育场', 22), ('大学生体育馆', 23), ('奥体中心', 24), 
                                        ('奥林匹克公园', 25), ('老山自行车赛场', 26), ('先龙坛体育馆', 27)])
    homedir = os.getcwd()
    
    now = time.ctime()
    print(now)
    nowstrp = time.strptime(now)
    
    outdir = homedir + '/Meteo/' 
    if not os.path.exists(outdir):
        os.makedirs(outdir)       
    outfile = outdir + time.strftime('%Y%m%d', nowstrp) + '.csv'
                
    for id in stations.values():
        st = station()
        st.name = list(stations.keys())[list(stations.values()).index(id)]
        st.acquire = time.strftime('%Y-%m-%d %H:%M:%S', nowstrp)
                           
        try:
            # 获取网页信息
            table = requestData(id)
            if(table):
                header = table[0]
                data = table[1:len(table)]
                for row in data:
                    st.dict['台站'] = st.name
                    for col in header:
                        st.dict[col] = row[header.index(col)]
                    st.dict['获取时间'] = st.acquire 
                    writeData(outfile, st.dict)
                    
                    for key, value in list(st.dict.items()):
                        print(('%s: %s' % (key, value)))
        except Exception as e:
            error = now + '\r\n' + st.name + '\r\n' + traceback.format_exc() + '\r\n'
            print(error)
            f = codecs.open('error.log', 'a', 'utf-8')
            f.writelines(error)
            f.close()