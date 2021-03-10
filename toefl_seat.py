from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
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
TOEFL_URL = 'https://toefl.neea.cn/login'
TOEFL_USERNAME = 'your username'
TOEFL_PASSWORD = 'your password'
PROXIES = {"http":"socks5://127.0.0.1:10808","https":"socks5://127.0.0.1:10808"}

STATE = ['暂满', '有位']

def update_database(data):
    print("开始更新数据库"
    
    # Use any database you like to store the info)
    db = mysql.connector.connect(
        host = "localhost",
        user = "ETSHelper",
        password = "_Yitiaoxianyu",
        database = "ETS"
    )
    change_log = []
    cursor = db.cursor()
    for sites in data:
        time = sites['time']
        city = sites['city']
        location = sites['location']
        site = sites['site']
        state = sites['state']
        day = sites['day']
        select_syntax = "SELECT time,city,location,site,state,day FROM TOEFL_seats WHERE time='{time}' AND site='{site}';".format(time=time, site=site)
        cursor.execute(select_syntax)
        res = cursor.fetchall()
        if len(res) == 0:
            change_log.append("{time} {day} {city} {location} {site} 考位变化情况: 不存在 → {new_state}".format(time=time, day=day, city=city, location=location, site=site, new_state=STATE[state]))
            insert_syntax = "INSERT INTO TOEFL_seats(time,city,location,site,state,day) VALUES ('{time}', '{city}', '{location}', '{site}', {state}, '{day}');".format(time=time, city=city, location=location, site=site, state=state, day=day)
            cursor.execute(insert_syntax)
        else:
            old_state = res[0][4]
            if old_state != state:
                change_log.append(
                    "{time} {day} {city} {location} {site} 考位变化情况: {old_state} → {new_state}".format(time=time, day=day, city=city, location=location, site=site, old_state=STATE[old_state], new_state=STATE[state]))
                update_syntax = "UPDATE TOEFL_seats SET state={state} WHERE time='{time}' AND site='{site}';".format(state=state, time=time, site=site)
                cursor.execute(update_syntax)

    db.commit()
    return change_log

def get_seats(driver, cookies):
    print("获取座位信息...")
    city_list = []
    date_list = []
    data = []
    city_names = driver.find_elements_by_xpath('//*[@id="centerProvinceCity"]/optgroup/option')
    for city_name in city_names:
        city_list.append(city_name.get_attribute("value"))
    test_dates = driver.find_elements_by_xpath('//*[@id="testDays"]/option')[1:]
    for test_date in test_dates:
        date_list.append(test_date.get_attribute("value"))

    session = requests.session()
    requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    for date in date_list:
        for city in city_list:
            url = "https://toefl.neea.cn/myHome/21270681/testSeat/queryTestSeats.json?city={city}&&testDay={date}".format(city=city, date=date)
            res = session.get(url)
            while (res.text[0] != "{"): res = session.get(url)
            print(res)
            dic = {}
            js = json.loads(res.text)
            if js["status"] == False:
                continue
            sites = list(js["testSeats"].values())[0]
            content = js["testDate"].split(" ")
            datetime = re.sub(r'[\u4e00-\u9fa5]', r'-', content[0])
            datetime = datetime[0:-1]
            datetime = datetime + " " + sites[0]["testTime"] + ":00"
            day = content[1]
            for site in sites:
                dic = {}
                dic["time"] = datetime
                dic["day"] = day
                dic["site"] = site["centerCode"]
                dic["city"] = site["cityCn"]
                dic["location"] = site["centerNameCn"]
                dic["state"] = site["seatStatus"]
                data.append(dic)

    return data

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

def get_verified(driver, first_try):
    driver.implicitly_wait(5)
    if first_try: driver.find_element_by_id("userName").send_keys(TOEFL_USERNAME)
    driver.find_element_by_id("textPassword").send_keys(TOEFL_PASSWORD)
    driver.find_element_by_id("verifyCode").click()
    time.sleep(3)
    driver.implicitly_wait(2)
    image = driver.find_element_by_id("chkImg").screenshot_as_png
    content = Image.open(BytesIO(image))
    content.save(PIC_PATH)

    '''
    # 使用打码平台（图鉴）来识别验证码（收费）
    img = Image.open(PIC_PATH)
    captcha_text = base64_api(uname='your username', pwd='your password', img=img)
    captcha_text.replace('6', 'G')
    captcha_text.replace('0', 'O')
    if captcha_text[-1] == ' ': captcha_text = captcha_text[0:-1]
    captcha_text = captcha_text.upper()
    if len(captcha_text) != 4: return False, captcha_text
    '''

    # 使用本地神经网络来识别验证码（免费）
    captcha_text = predict('TOEFL', 96, 30)

    print("验证码为: " + captcha_text)
    driver.find_element_by_id("verifyCode").send_keys(captcha_text)
    login = driver.find_element_by_id("btnLogin")
    ActionChains(driver).click(login).perform()
    time.sleep(1)
    return driver, driver.current_url == 'https://toefl.neea.cn/myHome/21270681/index', captcha_text

def login(driver):
    driver.get(TOEFL_URL)
    ready = False
    text = ""
    first_try = True
    cnt = 0
    while not ready and cnt < 5:
        driver, ready, text = get_verified(driver, first_try)
        first_try = False
        cnt = cnt + 1

    file = glob.glob(pathname='./captcha/data/TOEFL/train/*.png')
    output_path = "./captcha/data/TOEFL/train/" + text + "_" + str(len(file)) + ".png"
    os.rename(PIC_PATH, output_path)

    driver.implicitly_wait(5)
    driver.find_element_by_xpath('//*[@href="#!/testSeat"]').click()
    driver.implicitly_wait(5)
    Select(driver.find_element_by_id("centerProvinceCity")).select_by_value('BEIJING')
    Select(driver.find_element_by_id("testDays")).select_by_value('2020-12-20')
    time.sleep(2)
    driver.find_element_by_id("btnQuerySeat").click()
    time.sleep(5)
    cnt = 0
    while len(driver.find_elements_by_tag_name("h4")) == 1 and cnt < 5:
        cnt = cnt + 1
        Select(driver.find_element_by_id("centerProvinceCity")).select_by_value('BEIJING')
        Select(driver.find_element_by_id("testDays")).select_by_value('2020-12-20')
        time.sleep(2)
        driver.find_element_by_id("btnQuerySeat").click()
        time.sleep(5)
        print("进入考位查询失败，重试中...")

    cookies = {}
    content = driver.get_cookies()
    for cookie in content:
        cookies[cookie['name']] = cookie['value']
    print("进入考位查询成功！")
    return driver, cookies

def initalize():
    option = webdriver.FirefoxOptions()
    option.add_argument("--headless")
    # option.add_argument('--proxy-server=socks5://127.0.0.1:10808')
    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", options=option)
    return driver

def toefl_run():
    driver = initalize()  # initialize
    try:
        driver, cookies = login(driver) # login
        change_log = ['以下TOEFL考试考位状态刚刚发生了变化，请查收：']
        data = get_seats(driver, cookies)
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
    toefl_run()