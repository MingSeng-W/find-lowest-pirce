from selenium import webdriver
import time
import arrow
import random
import pymysql
import uuid
from apscheduler.schedulers.blocking import BlockingScheduler


def writeToDataBase(ipAdress, port ,loc, service, validateTime, cursor,db):
    print(ipAdress, port, loc, service, validateTime)
    sql= "INSERT INTO proxy( id, ip, port, loc, service, validate_time) VALUES(%s, %s,%s, %s, %s, %s)" 
    # try:
    cursor.execute(sql, (str(uuid.uuid1()), ipAdress, port, loc, service, validateTime))
    db.commit()
    # except:
    #     db.rollback()
    pass

def getPage(cursor ,db, num):
    option = webdriver.FirefoxOptions()
    option.set_headless(headless=True)
    driver = webdriver.Firefox(executable_path="./geckodriver",firefox_options=option)
    driver.set_window_size(1366,768)
    driver.get("http://www.89ip.cn/index_"+str(num)+".html")
    body = driver.find_element_by_tag_name('tbody')
    ips = body.find_elements_by_tag_name('tr')
    for ip in ips:
        item = ip.find_elements_by_tag_name('td')
        ipAdress = item[0].text
        port = item[1].text
        loc = item[2].text
        service = item[3].text
        validateTime = item[4].text
        # 写入数据库
        writeToDataBase(ipAdress, port ,loc, service, validateTime, cursor,db)
    driver.quit()   
    pass
def mainFunc():
    sched = BlockingScheduler()
    sched.add_job(handleMain, 'interval', seconds=200)
    sched.start()
    handleMain()
    pass

def handleMain(): 
    db = pymysql.connect("localhost","root", "mysql", "flights")
    cursor = db.cursor()
    count = 1
    while(count<4):
        getPage(cursor, db, count)
        time.sleep(random.randint(5,10))
        count = count +1
    db.close() 
    pass   
mainFunc()