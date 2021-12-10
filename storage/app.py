import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from inventory_count import InventoryCount
from checked_items import CheckedItems
import datetime
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import time
import os



if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"


with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)



app_config_ds = app_config['datastore']
DB_ENGINE = create_engine(f"mysql+pymysql://{app_config_ds['user']}:{app_config_ds['password']}@{app_config_ds['hostname']}:{app_config_ds['port']}/{app_config_ds['db']}")
logger.info(f"Connecting to DB. Hostname: {app_config_ds['hostname']}, Port:{app_config_ds['port']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def inventory_scan(body):
    session = DB_SESSION()
    inv_scan = InventoryCount(body["total_count"],
                             body["expected_count"],
                             body["items_missing"],
                             body["surplus"],
                             body["time_scanned"])

    session.add(inv_scan)
    session.commit()
    session.close()

    logger.debug(f"Stored event countevent request at {body['total_count']}, {body['time_scanned']}")

    return NoContent, 201


def get_inventory_count(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    results = session.query(InventoryCount).filter(and_(InventoryCount.date_created >= start_timestamp_datetime, InventoryCount.date_created < end_timestamp_datetime))
    results_list = []
    for r in results:
        results_list.append(r.to_dict())
    logger.debug(f'return {len(results_list)} count items')
    session.close()

    logger.info("query for inventory count events after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200


def check_item(body):
    session = DB_SESSION()

    chkd_items = CheckedItems(body["product_code"],
                              body["location"],
                              body["item_from"],
                              body["item_type"],
                              body["time_scanned"])


    session.add(chkd_items)
    session.commit()
    session.close()

    logger.debug(f"Stored event checkevent request at {body['product_code']}, {body['time_scanned']}")

    return NoContent, 201


def get_checked_item(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    results = session.query(CheckedItems).filter(and_(CheckedItems.date_created >= start_timestamp_datetime, CheckedItems.date_created < end_timestamp_datetime))
    results_list = []
    for r in results:
        results_list.append(r.to_dict())
    logger.debug(f'return {len(results_list)} checked items')
    session.close()

    logger.info("query for inventory check events after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])

    current_retry_count = 0
    while current_retry_count < app_config['retry']['max_retries']:
        try:
            logger.info(f"Connecting to Kafka: {current_retry_count}")
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config['events']['topic'])]
            break
        except:
            logger.error("Connection failed")
            time.sleep(app_config['retry']['sleep'])
            current_retry_count += 1

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg['payload']
        print(payload)
        if msg['type'] == 'count':
            inventory_scan(payload)
            logger.info("Added to count event")
        elif msg['type'] == 'check':
            check_item(payload)
            logger.info("Added to check event")

        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
