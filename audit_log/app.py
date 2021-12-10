import connexion
from pykafka import KafkaClient
import yaml
import logging
import logging.config
import json
from flask_cors import CORS, cross_origin
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



def get_inventory_count(index):
    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    
    logger.info("Retrieving count at index %d" % index)
    try:
        count_events = []

        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            print(msg)
            # find event at index + return event & 200
            if msg['type'] == 'count':
                count_events.append(msg)
                
        if index in range(0, len(count_events)):
            return count_events[index], 200
        else:
            
            return {"message": "Not found"}, 404


    except:
        logger.error("No more messages found")
        print()
    
    logger.error("Could not find count at index %d" % index)
    return {"message": "Not found"}, 404









def get_checked_items(index):
    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    
    logger.info("Retrieving checked item at index %d" % index)
    try:
        check_events = []

        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)

            # find event at index + return event & 200
            if msg['type'] == 'check':
                check_events.append(msg)
                
        if index in range(0, len(check_events)):
            return check_events[index], 200
        else:
            return {"message": "Not found"}, 404


    except:
        logger.error("No more messages found")
        print()
    
    logger.error("Could not find checked item at index %d" % index)
    return {"message": "Not found"}, 404

app = connexion.FlaskApp(__name__, specification_dir="")

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
