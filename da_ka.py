import http
import json
import os
import random
import re
import urllib
from http import cookiejar
from urllib import parse
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

schoolID=#学校ID
lng=#经度
lat=#纬度
address='#学校地址'
identity=0
bashDir='./'
signType=1
sfby = 1
zddlwz = address
msg_from = ''  # 发送方邮箱
passwd = ''    # 就是上面的授权码

#发送错误信息
def Send_Imei_Wrong(mail):
    msg = MIMEMultipart()
    conntent = "少爷,已经打过卡了！！！！"
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    msg['Subject'] = "少爷,已经打过卡了！！！！"
    msg['From'] = msg_from
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, mail, msg.as_string())

#发送成功信息
def Send_succes_run(mail):
    msg = MIMEMultipart()
    conntent = "少爷,今天打卡完啦！！！！"
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    msg['Subject'] = "少爷,今天打卡完啦！！！！"
    msg['From'] = msg_from
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, mail, msg.as_string())
#打卡主程序
def login(ids,mail):
    print('学号:'+str(ids))
    url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/public/homeQd?loginName=' + str(ids) + '&loginType=' + str(
        identity)
    if os.path.isdir(bashDir + 'cookie') == False:
        os.mkdir(bashDir + 'cookie')
    if os.path.isdir(bashDir + 'cookie/' + str(ids)) == False:
        os.mkdir(bashDir + 'cookie/' + str(ids))
    cookie_file = bashDir + 'cookie/' + str(ids) + '/cookie.txt'
    open(cookie_file, 'w+').close()
    cookie = http.cookiejar.MozillaCookieJar(cookie_file)
    cookies = urllib.request.HTTPCookieProcessor(cookie)  # 创建一个处理cookie的handler
    opener = urllib.request.build_opener(cookies)         # 创建一个opener
    request = urllib.request.Request(url=url)
    res = opener.open(request)
    verify(cookie)
    construction_post(lng, lat, address)
    sign_history(cookie)
    sign(cookie,mail)
    print('打卡结束')

def verify(cookie):
    url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/public/xslby'
    cookies = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookies)
    request = urllib.request.Request(url=url, method='POST')
    res = opener.open(request)
    info_html = res.read().decode()
    if '学生签到' not in info_html:
        return False
    else:
        print(str('检测成功！'))
    return True

def sign_history(cookie):
    url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/studentQd/pageStudentQdInfoByXh'
    cookies = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookies)
    request = urllib.request.Request(url=url, method='POST')
    res = opener.open(request)
    info_json = res.read().decode()
    print(info_json)

def construction_post(lng1, lat1, address):
    global lng, lat, zddlwz, signPostInfo
    if signType == 0:
        # 随机偏移1m
        lng = round(float(lng1) + random.uniform(-0.000010, +0.000010), 6)
        lat = round(float(lat1) + random.uniform(-0.000010, +0.000010), 6)
        zddlwz = address
    else:
        # 随机偏移11m
        lng = round(float(lng) + random.uniform(-0.000100, +0.000100), 6)
        lat = round(float(lat) + random.uniform(-0.000100, +0.000100), 6)
        address = zddlwz
    # 通过百度地图api获取所在的省市区等
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=80smLnoLWKC9ZZWNLL6i7boKiQeVNEbq&output=json&coordtype' \
          '=wgs84ll&location=' + str(lat) + ',' + str(lng)
    res = requests.get(url)
    # 解析api返回的json数据
    res_dic = json.loads(res.text)
    add_dic = res_dic['result']['addressComponent']
    # 取得省市区
    province = add_dic['province']
    city = add_dic['city']
    district = add_dic['district']
    # 一层层剖析尽量获取到最小的街道
    try:
        regular = '(?<=' + district + ').+?(?=$)'
        street = str(re.search(regular, address).group(0))
    except AttributeError:
        try:
            regular = '(?<=' + city + ').+?(?=$)'
            street = str(re.search(regular, address).group(0))
        except AttributeError:
            try:
                regular = '(?<=' + province + ').+?(?=$)'
                street = str(re.search(regular, address).group(0))
            except AttributeError:
                street = address
    province = parse.quote(province)
    city = parse.quote(city)
    district = parse.quote(district)
    street = parse.quote(street)
    address = parse.quote(address)
    post = 'province=' + province + '&city=' + city + '&district=' + district + '&street=' + street + '&xszt=0&jkzk=0' \
                                                                                                      '&jkzkxq=&sfgl=1&gldd=&mqtw=0&mqtwxq=&zddlwz=' + address + '&sddlwz=&bprovince=' + province + '&bcity=' \
           + city + '&bdistrict=' + district + '&bstreet=' + street + '&sprovince=' + province + '&scity=' + city + \
           '&sdistrict=' + district + '&lng=' + str(lng) + '&lat=' + str(lat) + '&sfby=' + str(sfby)
    signPostInfo = post
    signPostInfo = signPostInfo.encode('utf-8')
def sign(cookie,mail):
    url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/studentQd/saveStu'
    cookies = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookies)
    request = urllib.request.Request(url=url, method='POST', data=signPostInfo)
    res = opener.open(request)
    res = res.read().decode()
    if '1001' in res:
        print('打卡状态:打卡成功')
        Send_succes_run(mail)
    elif '1002' in res:
        print('打卡状态:今天已经打卡啦')
        Send_Imei_Wrong(mail)
    else:
        print('打卡状态:打卡有些不对劲')
        Send_Imei_Wrong(mail)
# 普通运行入口
if __name__ == "__main__":
    #学号
    ID1 = #学号
    ID2 = #学号
    login(ID1,'#邮箱')
    login(ID2,'#邮箱')
    
