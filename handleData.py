import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymysql

db = pymysql.connect("localhost","root", "mysql", "flights")
sql = "SELECT * FROM flights ORDER BY day ASC"
df = pd.read_sql(sql,db)
plt.scatter(np.arange(len(df['price'])),df['price'])
plt.show()