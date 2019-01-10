import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymysql
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def getLowestPriceForADay(data):
    # 找出一天的最低价
    res = []
    tmp = {}
    currrentDay = ""
    for item in data: 
         if currrentDay==item['day']:
             tmp[currrentDay].append(item)
         else:
             currrentDay = item['day']
             tmp[currrentDay] = []
             tmp[currrentDay].append(item)
    for key in tmp:
        res.append(sorted(tmp[key], key=lambda x: x['price'])[0])
    return res 

db = pymysql.connect("localhost","root", "mysql", "flights", cursorclass = pymysql.cursors.DictCursor, charset='utf8')
cursor = db.cursor()
sql = "SELECT * FROM flights ORDER BY day ASC"
cursor.execute(sql)
data = getLowestPriceForADay(cursor.fetchall())
db.close()
df = pd.DataFrame(data)
prices = [x for x in df['price']]
prices[0] = 150
ff = pd.DataFrame(prices, columns=['price']).reset_index()
X = StandardScaler().fit_transform(ff)
dbscan = DBSCAN(eps=1.5, min_samples=1).fit(X)
labels = dbscan.labels_
uniq_labels = set(labels)
clusters = len(set(labels))
colors = plt.cm.Spectral(np.linspace(0,1,len(uniq_labels)))
plt.subplots(figsize=(12,8))
for k , c in zip(uniq_labels,colors):
    class_member_mask =(labels ==k)
    xy = X[class_member_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c, markeredgecolor='k', markersize=14)
    plt.title("total clusters:{}".format(clusters), fontsize=14, y=1.01) 
plt.show()       
