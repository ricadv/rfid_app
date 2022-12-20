import mysql.connector

conn = mysql.connector.connect(user='admin', password='Admin!234567',
                               host='ec2-34-223-195-171.us-west-2.compute.amazonaws.com',
                               database='inventory')

c = conn.cursor()
c.execute('''
          DROP TABLE inventory_count, checked_items
          ''')



conn.commit()
conn.close()
