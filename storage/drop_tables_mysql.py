import mysql.connector

conn = mysql.connector.connect(user='admin', password='Admin!234567',
                               host='rfid.ricadevera.com',
                               database='inventory')

c = conn.cursor()
c.execute('''
          DROP TABLE inventory_count, checked_items
          ''')



conn.commit()
conn.close()
