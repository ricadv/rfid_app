import mysql.connector

conn = mysql.connector.connect(user='admin', password='Admin!234567',
                               host='acit3855.westus.cloudapp.azure.com',
                               database='inventory')

c = conn.cursor()
c.execute('''
          DROP TABLE inventory_count, checked_items
          ''')



conn.commit()
conn.close()
