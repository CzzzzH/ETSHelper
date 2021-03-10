from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from io import BytesIO
from captcha.predict import predict
import mysql.connector
import requests
import time
import json
import re
import os
import sys
import glob
import base64
import traceback

PIC_PATH = './captcha/predict/XXXX_captcha.png'
VERIFY_URL = 'http://127.0.0.1:6000/b'
GRE_URL = 'https://gre.neea.cn/'
GRE_SEAT_URL = [
                    'https://gre.neea.cn/testSites.do?p=testSites&m=ajax&ym=2020-09&neeaID=71591326&cities=BEIJING_BEIJING;TIANJIN_TIANJIN;HEBEI_SHIJIAZHUANG;SHANXI_TAIYUAN;ANHUI_HEFEI;FUJIAN_FUZHOU;JIANGSU_NANJING;JIANGSU_SUZHOU;JIANGSU_NANTONG;JIANGSU_YANGZHOU;JIANGSU_XUZHOU;JIANGXI_NANCHANG;SHANDONG_JINAN;SHANDONG_QINGDAO;SHANDONG_WEIFANG;SHANDONG_LINYI;SHANGHAI_SHANGHAI;ZHEJIANG_HANGZHOU;ZHEJIANG_NINGBO;ZHEJIANG_WENZHOU;GUANGDONG_GUANGZHOU;GUANGDONG_SHENZHEN;GUANGDONG_DONGGUAN;HENAN_ZHENGZHOU;HUBEI_WUHAN;HUNAN_CHANGSHA;HEILONGJIANG_HAERBIN;JILIN_CHANGCHUN;LIAONING_DALIAN;LIAONING_SHENYANG;GANSU_LANZHOU;NEIMENGGU_HUHEHAOTE;SHAANXI_XIAN;CHONGQING_CHONGQING;SICHUAN_CHENGDU;YUNNAN_KUNMING;&citiesNames=%E5%8C%97%E4%BA%AC;%E5%A4%A9%E6%B4%A5;%E7%9F%B3%E5%AE%B6%E5%BA%84;%E5%A4%AA%E5%8E%9F;%E5%90%88%E8%82%A5;%E7%A6%8F%E5%B7%9E;%E5%8D%97%E4%BA%AC;%E8%8B%8F%E5%B7%9E;%E5%8D%97%E9%80%9A;%E6%89%AC%E5%B7%9E;%E5%BE%90%E5%B7%9E;%E5%8D%97%E6%98%8C;%E6%B5%8E%E5%8D%97;%E9%9D%92%E5%B2%9B;%E6%BD%8D%E5%9D%8A;%E4%B8%B4%E6%B2%82;%E4%B8%8A%E6%B5%B7;%E6%9D%AD%E5%B7%9E;%E5%AE%81%E6%B3%A2;%E6%B8%A9%E5%B7%9E;%E5%B9%BF%E5%B7%9E;%E6%B7%B1%E5%9C%B3;%E4%B8%9C%E8%8E%9E;%E9%83%91%E5%B7%9E;%E6%AD%A6%E6%B1%89;%E9%95%BF%E6%B2%99;%E5%93%88%E5%B0%94%E6%BB%A8;%E9%95%BF%E6%98%A5;%E5%A4%A7%E8%BF%9E;%E6%B2%88%E9%98%B3;%E5%85%B0%E5%B7%9E;%E5%91%BC%E5%92%8C%E6%B5%A9%E7%89%B9;%E8%A5%BF%E5%AE%89;%E9%87%8D%E5%BA%86;%E6%88%90%E9%83%BD;%E6%98%86%E6%98%8E;&whichFirst=AS&isFilter=0&isSearch=1',
                    'https://gre.neea.cn/testSites.do?p=testSites&m=ajax&ym=2020-10&neeaID=71591326&cities=BEIJING_BEIJING;TIANJIN_TIANJIN;HEBEI_SHIJIAZHUANG;SHANXI_TAIYUAN;ANHUI_HEFEI;FUJIAN_FUZHOU;JIANGSU_NANJING;JIANGSU_SUZHOU;JIANGSU_NANTONG;JIANGSU_YANGZHOU;JIANGSU_XUZHOU;JIANGXI_NANCHANG;SHANDONG_JINAN;SHANDONG_QINGDAO;SHANDONG_WEIFANG;SHANDONG_LINYI;SHANGHAI_SHANGHAI;ZHEJIANG_HANGZHOU;ZHEJIANG_NINGBO;ZHEJIANG_WENZHOU;GUANGDONG_GUANGZHOU;GUANGDONG_SHENZHEN;GUANGDONG_DONGGUAN;HENAN_ZHENGZHOU;HUBEI_WUHAN;HUNAN_CHANGSHA;HEILONGJIANG_HAERBIN;JILIN_CHANGCHUN;LIAONING_DALIAN;LIAONING_SHENYANG;GANSU_LANZHOU;NEIMENGGU_HUHEHAOTE;SHAANXI_XIAN;CHONGQING_CHONGQING;SICHUAN_CHENGDU;YUNNAN_KUNMING;&citiesNames=%E5%8C%97%E4%BA%AC;%E5%A4%A9%E6%B4%A5;%E7%9F%B3%E5%AE%B6%E5%BA%84;%E5%A4%AA%E5%8E%9F;%E5%90%88%E8%82%A5;%E7%A6%8F%E5%B7%9E;%E5%8D%97%E4%BA%AC;%E8%8B%8F%E5%B7%9E;%E5%8D%97%E9%80%9A;%E6%89%AC%E5%B7%9E;%E5%BE%90%E5%B7%9E;%E5%8D%97%E6%98%8C;%E6%B5%8E%E5%8D%97;%E9%9D%92%E5%B2%9B;%E6%BD%8D%E5%9D%8A;%E4%B8%B4%E6%B2%82;%E4%B8%8A%E6%B5%B7;%E6%9D%AD%E5%B7%9E;%E5%AE%81%E6%B3%A2;%E6%B8%A9%E5%B7%9E;%E5%B9%BF%E5%B7%9E;%E6%B7%B1%E5%9C%B3;%E4%B8%9C%E8%8E%9E;%E9%83%91%E5%B7%9E;%E6%AD%A6%E6%B1%89;%E9%95%BF%E6%B2%99;%E5%93%88%E5%B0%94%E6%BB%A8;%E9%95%BF%E6%98%A5;%E5%A4%A7%E8%BF%9E;%E6%B2%88%E9%98%B3;%E5%85%B0%E5%B7%9E;%E5%91%BC%E5%92%8C%E6%B5%A9%E7%89%B9;%E8%A5%BF%E5%AE%89;%E9%87%8D%E5%BA%86;%E6%88%90%E9%83%BD;%E6%98%86%E6%98%8E;&whichFirst=AS&isFilter=0&isSearch=1',
                    'https://gre.neea.cn/testSites.do?p=testSites&m=ajax&ym=2020-11&neeaID=71591326&cities=BEIJING_BEIJING;TIANJIN_TIANJIN;HEBEI_SHIJIAZHUANG;SHANXI_TAIYUAN;ANHUI_HEFEI;FUJIAN_FUZHOU;JIANGSU_NANJING;JIANGSU_SUZHOU;JIANGSU_NANTONG;JIANGSU_YANGZHOU;JIANGSU_XUZHOU;JIANGXI_NANCHANG;SHANDONG_JINAN;SHANDONG_QINGDAO;SHANDONG_WEIFANG;SHANDONG_LINYI;SHANGHAI_SHANGHAI;ZHEJIANG_HANGZHOU;ZHEJIANG_NINGBO;ZHEJIANG_WENZHOU;GUANGDONG_GUANGZHOU;GUANGDONG_SHENZHEN;GUANGDONG_DONGGUAN;HENAN_ZHENGZHOU;HUBEI_WUHAN;HUNAN_CHANGSHA;HEILONGJIANG_HAERBIN;JILIN_CHANGCHUN;LIAONING_DALIAN;LIAONING_SHENYANG;GANSU_LANZHOU;NEIMENGGU_HUHEHAOTE;SHAANXI_XIAN;CHONGQING_CHONGQING;SICHUAN_CHENGDU;YUNNAN_KUNMING;&citiesNames=%E5%8C%97%E4%BA%AC;%E5%A4%A9%E6%B4%A5;%E7%9F%B3%E5%AE%B6%E5%BA%84;%E5%A4%AA%E5%8E%9F;%E5%90%88%E8%82%A5;%E7%A6%8F%E5%B7%9E;%E5%8D%97%E4%BA%AC;%E8%8B%8F%E5%B7%9E;%E5%8D%97%E9%80%9A;%E6%89%AC%E5%B7%9E;%E5%BE%90%E5%B7%9E;%E5%8D%97%E6%98%8C;%E6%B5%8E%E5%8D%97;%E9%9D%92%E5%B2%9B;%E6%BD%8D%E5%9D%8A;%E4%B8%B4%E6%B2%82;%E4%B8%8A%E6%B5%B7;%E6%9D%AD%E5%B7%9E;%E5%AE%81%E6%B3%A2;%E6%B8%A9%E5%B7%9E;%E5%B9%BF%E5%B7%9E;%E6%B7%B1%E5%9C%B3;%E4%B8%9C%E8%8E%9E;%E9%83%91%E5%B7%9E;%E6%AD%A6%E6%B1%89;%E9%95%BF%E6%B2%99;%E5%93%88%E5%B0%94%E6%BB%A8;%E9%95%BF%E6%98%A5;%E5%A4%A7%E8%BF%9E;%E6%B2%88%E9%98%B3;%E5%85%B0%E5%B7%9E;%E5%91%BC%E5%92%8C%E6%B5%A9%E7%89%B9;%E8%A5%BF%E5%AE%89;%E9%87%8D%E5%BA%86;%E6%88%90%E9%83%BD;%E6%98%86%E6%98%8E;&whichFirst=AS&isFilter=0&isSearch=1',
                    'https://gre.neea.cn/testSites.do?p=testSites&m=ajax&ym=2020-12&neeaID=71591326&cities=BEIJING_BEIJING;TIANJIN_TIANJIN;HEBEI_SHIJIAZHUANG;SHANXI_TAIYUAN;ANHUI_HEFEI;FUJIAN_FUZHOU;JIANGSU_NANJING;JIANGSU_SUZHOU;JIANGSU_NANTONG;JIANGSU_YANGZHOU;JIANGSU_XUZHOU;JIANGXI_NANCHANG;SHANDONG_JINAN;SHANDONG_QINGDAO;SHANDONG_WEIFANG;SHANDONG_LINYI;SHANGHAI_SHANGHAI;ZHEJIANG_HANGZHOU;ZHEJIANG_NINGBO;ZHEJIANG_WENZHOU;GUANGDONG_GUANGZHOU;GUANGDONG_SHENZHEN;GUANGDONG_DONGGUAN;HENAN_ZHENGZHOU;HUBEI_WUHAN;HUNAN_CHANGSHA;HEILONGJIANG_HAERBIN;JILIN_CHANGCHUN;LIAONING_DALIAN;LIAONING_SHENYANG;GANSU_LANZHOU;NEIMENGGU_HUHEHAOTE;SHAANXI_XIAN;CHONGQING_CHONGQING;SICHUAN_CHENGDU;YUNNAN_KUNMING;&citiesNames=%E5%8C%97%E4%BA%AC;%E5%A4%A9%E6%B4%A5;%E7%9F%B3%E5%AE%B6%E5%BA%84;%E5%A4%AA%E5%8E%9F;%E5%90%88%E8%82%A5;%E7%A6%8F%E5%B7%9E;%E5%8D%97%E4%BA%AC;%E8%8B%8F%E5%B7%9E;%E5%8D%97%E9%80%9A;%E6%89%AC%E5%B7%9E;%E5%BE%90%E5%B7%9E;%E5%8D%97%E6%98%8C;%E6%B5%8E%E5%8D%97;%E9%9D%92%E5%B2%9B;%E6%BD%8D%E5%9D%8A;%E4%B8%B4%E6%B2%82;%E4%B8%8A%E6%B5%B7;%E6%9D%AD%E5%B7%9E;%E5%AE%81%E6%B3%A2;%E6%B8%A9%E5%B7%9E;%E5%B9%BF%E5%B7%9E;%E6%B7%B1%E5%9C%B3;%E4%B8%9C%E8%8E%9E;%E9%83%91%E5%B7%9E;%E6%AD%A6%E6%B1%89;%E9%95%BF%E6%B2%99;%E5%93%88%E5%B0%94%E6%BB%A8;%E9%95%BF%E6%98%A5;%E5%A4%A7%E8%BF%9E;%E6%B2%88%E9%98%B3;%E5%85%B0%E5%B7%9E;%E5%91%BC%E5%92%8C%E6%B5%A9%E7%89%B9;%E8%A5%BF%E5%AE%89;%E9%87%8D%E5%BA%86;%E6%88%90%E9%83%BD;%E6%98%86%E6%98%8E;&whichFirst=AS&isFilter=0&isSearch=1',
                ]
PROXIES = {"http":"socks5://127.0.0.1:10808","https":"socks5://127.0.0.1:10808"}
GRE_USERNAME = 'your username'
GRE_PASSWORD = 'yoru password'
STATE = ['暂满', '有位', '截止']

def update_database(data):
    print("开始更新数据库")

    # Use any database you like to store the info
    db = mysql.connector.connect(
        host = "localhost",
        user = "ETSHelper",
        password = "_Yitiaoxianyu",
        database = "ETS"
    )
    
    change_log = []
    cursor = db.cursor()
    for citys in data:
        city = citys["city"]
        for date in citys["dates"]:
            bjtime = date["bjTime"]
            content = bjtime.split(" ")
            time = re.sub(r'[\u4e00-\u9fa5]', r'-', content[0])
            time = time[0:-1]
            time = time + " " + content[3]
            day = content[1]
            for sites in date["sites"]:
                site = sites["siteCode"]
                location = sites["siteName"]
                if sites["isClosed"] == 1: state = 2
                else: state = sites["realSeats"]
                select_syntax = "SELECT time,city,location,site,state,day FROM GRE_seats WHERE time='{time}' AND site='{site}';".format(time=time, site=site)
                cursor.execute(select_syntax)
                res = cursor.fetchall()
                if len(res) == 0:
                    change_log.append("{time} {day} {city} {location} {site} 考位变化情况: 不存在 → {new_state}".format(time=time, day=day, city=city, location=location, site=site, new_state=STATE[state]))
                    insert_syntax = "INSERT INTO GRE_seats(time,city,location,site,state,day) VALUES ('{time}', '{city}', '{location}', '{site}', {state}, '{day}');".format(time=time, city=city, location=location, site=site, state=state, day=day)
                    cursor.execute(insert_syntax)
                else:
                    old_state = res[0][4]
                    if old_state != state:
                        change_log.append("{time} {day} {city} {location} {site} 考位变化情况: {old_state} → {new_state}".format(time=time, day=day, city=city, location=location, site=site, old_state=STATE[old_state], new_state=STATE[state]))
                        update_syntax = "UPDATE GRE_seats SET state={state} WHERE time='{time}' AND site='{site}';".format(state=state, time=time, site=site)
                        cursor.execute(update_syntax)
    db.commit()
    return change_log

def get_seats(cookies, month):
    print("获取座位信息...")
    res = requests.get(GRE_SEAT_URL[month], cookies=cookies)
    while (res.text[0] != "["):
        time.sleep(1)
        res = requests.get(GRE_SEAT_URL[month], cookies=cookies)
    js = json.loads(res.text)
    return js

def base64_api(uname, pwd,  img):
    img = img.convert('RGB')
    buffered = BytesIO()
    img.save(buffered, format="png")
    if sys.version_info.major >= 3:
        b64 = str(base64.b64encode(buffered.getvalue()), encoding='utf-8')
    else:
        b64 = str(base64.b64encode(buffered.getvalue()))
    data = {"username": uname, "password": pwd, "image": b64, "typeid": "7"}
    result = json.loads(requests.post("http://api.ttshitu.com/base64", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        return result["message"]

def get_verified(driver):
    driver.find_element_by_id("neeaId").send_keys(GRE_USERNAME)
    driver.find_element_by_id("password").send_keys(GRE_PASSWORD)
    driver.find_element_by_id("checkImageCode").click()
    driver.implicitly_wait(10)
    image = driver.find_element_by_id("chkImg").screenshot_as_png
    content = Image.open(BytesIO(image))
    content.save(PIC_PATH)

    '''
    # 使用打码平台（图鉴）来识别验证码（收费）
    img = Image.open(PIC_PATH)
    captcha_text = base64_api(uname='your username', pwd='your password', img=img)
    captcha_text.replace('6', 'G')
    captcha_text.replace('0', 'O')
    if (captcha_text[-1] == ' '): captcha_text = captcha_text[0:-1]
    captcha_text = captcha_text.upper()
    if (len(captcha_text) != 4): return False, captcha_text
    '''

    # 使用本地神经网络来识别验证码（免费）
    captcha_text = predict('GRE', 80, 25)

    print("验证码为: " + captcha_text)
    driver.find_element_by_id("checkImageCode").send_keys(captcha_text)
    login = driver.find_element_by_xpath('//*[@id="loginForm"]/div[5]/input')
    ActionChains(driver).click(login).perform()
    driver.implicitly_wait(5)
    try:
        driver.find_element_by_tag_name('h2')
    except:
        return False, captcha_text

    return True, captcha_text

def login(driver):
    driver.get(GRE_URL)
    driver.implicitly_wait(10)
    ready = False
    text = ""
    cnt = 0
    while not ready and cnt < 5:
        try:
            ready, text = get_verified(driver)
        except:
            driver.find_element_by_id("chkImg").click()
            cnt = cnt + 1
    file = glob.glob(pathname='./captcha/data/GRE/train/*.png')
    output_path = "./captcha/data/GRE/train/" + text + "_" + str(len(file) + 2105) + ".png"
    os.rename(PIC_PATH, output_path)
    cookies = {}
    time.sleep(3)
    content = driver.get_cookies()
    for cookie in content:
        cookies[cookie['name']] = cookie['value']
    return cookies

def initalize():
    option = webdriver.FirefoxOptions()
    option.add_argument("--headless")
    # option.add_argument('--proxy-server=socks5://127.0.0.1:10808')
    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", options=option)
    return driver

def gre_run():
    driver = initalize()  # initialize
    try:
        cookies = login(driver) # login
        change_log = ['以下GRE考试考位状态刚刚发生了变化，请查收：']
        for i in range(5):
            data = get_seats(cookies, i)
            change_log += update_database(data) # get data
        # driver.close()
        return change_log
    except:
        print(traceback.format_exc())
        change_log = ['更新失败']
        # driver.close()
        return change_log

if __name__ == '__main__':
    # download_captcha()
    gre_run()