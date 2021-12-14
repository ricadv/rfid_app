<h1>Containerized RFID Events Processing Application</h1>

<h3>The Application</h3>
<p>This application receives two types of events from Radio Frequency Identification (RFID) scanners that keep track of store inventory, including the location of individual items within the store.</p>

<p>One event is an inventory scan which occurs hourly during normal hours and every half an hour during peak times (midday on weekends and holidays). Another event is a check in/out which occurs whenever an item is moved from one area of the store (when scanned at an RFID gate e.g. back room to stage room or stage room to “purchased”). This event will also update the inventory count when the item is sold.</p>

<h3>End Users + Value</h3>
The primary users will be the Sales Associates who will need to know where the items are and whether they have a specific item in stock. The Finance team will also benefit as they will be able to use the readings for their financial reports. Another value it can bring is the tracking of individual items and what is getting sold.

<h3>Microservices Architecture</h3>
The majority of the code is written in Python. Each service pulls from external configuration files (openapi.yml, app_conf.yml) and logs to an app.log file.

<h4>Receiver Service</h4>
This service is fed mock events from JMeter through a Kafka stream which is then stored into a MySQL database.

<h4>Storage Service</h4>
<p>This service creates a table, if it does not yet exist, to store each type of event’s properties.</p>

The inventory_count table has fields such as:
<ul>
	<li>total_count - the current count of the back room inventory during a scheduled scan</li>
	<li>expected_count - calculated from the last total_count and the number of items checked in or out of the back room</li>
	<li>items_missing - the difference between expected_count and total_count</li>
	<li>surplus - the difference between total_count and expected_count</li>
	<li>time_scanned - time that the scan occured</li>
	<li>date_created - datetime that the scan was stored in the database</li>
</ul>

The checked_items table has fields such as:
<ul>
	<li>product_code - electronic product code (epc) which identifies a specific item</li>
	<li>location - current location of the item, i.e where it’s getting checked into</li>
	<li>item_from - the location from which the item came, i.e. where the item is getting checked out of</li>
	<li>item_type - the categorical type of item it is, e.g. pants, jacket, accessory, etc.</li>
	<li>time_scanned - time that the scan occured</li>
	<li>date_created - datetime that the scan was stored in the database</li>
</ul>

<h4>Processing Service</h4>
In this service, data is pulled from the database and used to state some statistics regarding the events stored. For example, we calculate the total number scans (inventory_count instances), the total number of items checked (checked_items instances), the max items_missing value, the max surplus value, and the datetime of the last time these stats were updated.

<h4>Audit Log Service</h4>
In this service, we make it possible to pull individual rows/instances from each event‘s table by their index.

<h4>Dashboard Service</h4>
This service provides an interface to the application’s Processing and Audit Log services, showing the app’s statistics and a single row/instance in each table chosen by a randomized index. The DNS is mapped to an AWS EC2 address.

<h3>Deployment</h3>
This application is deployed using Docker containers set up by a docker-compose file within the deployment directory.
