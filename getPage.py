from selenium import webdriver
import time
import arrow
import random
import pymysql
import uuid
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def getThreeMonthArr():
    res= []
    startDay = arrow.now().shift(days=1)
    endDayString = startDay.shift(months=3).format('YYYY-MM-DD')
    countDay = startDay
    while(countDay.format('YYYY-MM-DD')!=endDayString):
        res.append(countDay.format('YYYY-MM-DD'))
        countDay = countDay.shift(days=1)
    return res

def writeToDataBase(price, airCompany, startHour, endHour, startAirPort, endAirPort,  onTimeRate, durationTime, day,cursor, db):
    print(price, airCompany, startHour, endHour, startAirPort, endAirPort,  onTimeRate, durationTime)
    sql= "INSERT INTO flights(id, price, air_company, duration_time, on_time_rate, start_hour, end_hour, start_air_port, end_air_port, day) VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)" 
    try:
        cursor.execute(sql, (str(uuid.uuid1()), price, airCompany, durationTime, onTimeRate, startHour, endHour, startAirPort, endAirPort, day))
        db.commit()
    except:
        db.rollback()
    pass

def getPage(day, cursor ,db):
    sql = "SELECT ip, port, validate_time FROM  proxy ORDER BY validate_time DESC LIMIT 20 "
    cursor.execute(sql)
    proxys = cursor.fetchall()
    proxy = random.choice(proxys)
    print(proxy)
    profile = webdriver.FirefoxProfile()
    option = webdriver.FirefoxOptions()
    # option.set_headless(headless=True)
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('permissions.default.image', 0)
    profile.set_preference('permissions.default.stylesheet', 0)
    profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
    profile.set_preference('network.proxy.http',proxy[0])
    profile.set_preference('network.proxy.http_port',proxy[1])
    profile.update_preferences()
    driver = webdriver.Firefox(executable_path="./geckodriver", firefox_profile=profile)
    driver.set_window_size(1366,768)
    driver.set_page_load_timeout(30)
    flights= []
    try:
        driver.get("http://flight.tuniu.com/domestic/list/BJS_SHA_ST_1_0_0?deptDate="+day)
    except:
        print("超时")
        deleteSql = "DELETE FROM proxy WHERE ip = %s"
        cursor.execute(deleteSql,(proxy[0]))
        db.commit()
        driver.quit()  
        getPage(day, cursor, db)
        return  
    flights = driver.find_elements_by_class_name("J-flightlist")
    driver.save_screenshot("tuniu.png")
    for flight in flights:
        price = flight.find_element_by_class_name("num").text
        airCompany  = flight.find_element_by_class_name("aircom").text
        hours = flight.find_elements_by_class_name("hours")
        ariport = flight.find_elements_by_class_name("airport")
        durationTime = flight.find_element_by_class_name("durationTime").text
        onTimeRateOuter =  flight.find_element_by_class_name("rateWrap")
        onTimeRate = onTimeRateOuter.find_element_by_tag_name("li").text
        startHour = hours[0].text
        endHour = hours[1].text
        startAirPort = ariport[0].text
        endAirPort = ariport[1].text
        # 写入数据库
        writeToDataBase(price, airCompany, startHour, endHour, startAirPort, endAirPort, onTimeRate, durationTime, day, cursor,db)
    driver.quit()   
    pass
def mainFunc():
    days = getThreeMonthArr()
    db = pymysql.connect("localhost","root", "mysql", "flights")
    cursor = db.cursor()
    for day in days:
      print(day)
      getPage(day, cursor, db)
      time.sleep(random.randint(2,3))
    db.close() 
    pass        
mainFunc()