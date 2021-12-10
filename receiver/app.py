import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
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


current_retry_count = 0

while current_retry_count < app_config['retry']['max_retries']:
    try:
        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
        break
    except:
        logger.error("Connection to Kafka failed")
        time.sleep(app_config['retry']['sleep'])
        current_retry_count += 1




def inventory_scan(body):

    logger.info(f"Received event countevent request at {body['total_count']}, {body['time_scanned']}")
    headers = { 'content-type': 'application/json' }
    # response = requests.post(app_config['countevent']['url'], json=body, headers=headers)



    msg = { "type": "count",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"Returned event countevent response at {body['total_count']}, {body['time_scanned']} with status code 201")
    return NoContent, 201
        


def check_item(body):

    logger.info(f"Received event checkevent request at {body['product_code']}, {body['time_scanned']}")
    headers = { 'content-type': 'application/json' }
    # response = requests.post(app_config['checkevent']['url'], json=body, headers=headers)


    msg = { "type": "check",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"Returned event checkevent response at {body['product_code']}, {body['time_scanned']} with status 201")
    return NoContent, 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml', base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
