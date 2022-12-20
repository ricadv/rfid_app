import mysql.connector

conn = mysql.connector.connect(user='admin', password='Admin!234567',
                               host='ec2-34-223-195-171.us-west-2.compute.amazonaws.com',
                               database='inventory')

c = conn.cursor()


c.execute('''
          CREATE TABLE inventory_count
          (id INT NOT NULL AUTO_INCREMENT,
           total_count INT NOT NULL,
           expected_count INT NOT NULL,
           items_missing INTEGER NOT NULL,
           surplus INTEGER NOT NULL,
           time_scanned VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT inventory_count_pk PRIMARY KEY (id))
          ''')

c.execute('''
          CREATE TABLE checked_items
          (id INT NOT NULL AUTO_INCREMENT, 
           product_code VARCHAR(250) NOT NULL,
           location VARCHAR(100) NOT NULL,
           item_from VARCHAR(100) NOT NULL,
           item_type VARCHAR(100) NOT NULL,
           time_scanned VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT checked_items_pk PRIMARY KEY (id))
          ''')


conn.commit()
conn.close()
