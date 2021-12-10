import connexion
import requests
import yaml
import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
import os
import logging
import logging.config
from flask_cors import CORS, cross_origin



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

data_json = app_config['datastore']['filename']



def get_stats():
    logger.info("Stats request starting")
    if os.path.isfile(data_json):
        f = open(data_json, 'r')
        sdict = json.load(f)
        f.close()
        logger.debug(f"Returned stats: {sdict}")
        logger.info("Request fulfilled")
        return sdict, 200

    else:
        return "Statistics do not exist", 404





def populate_stats():
    logger.info("Starting periodic processing")

    stats_dict = {}
    if os.path.isfile(data_json):
        f = open(data_json, 'r')
        stats_dict = json.load(f)
        f.close()
    else:
        stats_dict["num_scans"] = 0
        stats_dict["num_checked"] = 0
        stats_dict["max_items_missing"] = 0
        stats_dict["max_surplus"] = 0
        stats_dict["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    get_count_res = requests.get(app_config['eventstore']['url'] + "/inventory/count?start_timestamp=" + stats_dict['last_updated'] + "&end_timestamp=" + current_timestamp)
    get_checked_items_res = requests.get(app_config['eventstore']['url'] + "/inventory/checked?start_timestamp=" + stats_dict['last_updated'] + "&end_timestamp=" + current_timestamp)

    print(get_count_res.json())
    stats_dict['num_scans'] += len(get_count_res.json())
    stats_dict['num_checked'] += len(get_checked_items_res.json())

    m_list = []
    for i in get_count_res.json():
        print(i)
        m_list.append(i['items_missing'])

    if len(m_list) != 0:
        stats_dict['max_items_missing'] = max(m_list)


    s_list = []
    for i in get_count_res.json():
        s_list.append(i['surplus'])

    if len(s_list) != 0:
        stats_dict['max_surplus'] = max([i['surplus'] for i in get_count_res.json()])


    stats_dict["last_updated"] = current_timestamp



    json_data = json.dumps(stats_dict)
    new_data_json = open(data_json, 'w')
    new_data_json.write(json_data)
    new_data_json.close()


    logger.info(f"Updated stats at {stats_dict['last_updated']} with {len(get_count_res.json()) + len(get_checked_items_res.json())} events")
    if get_count_res.status_code != 200 or get_checked_items_res.status_code != 200:
        logger.error("Error in response")

    logger.debug(f"New stat values: {stats_dict}")
    logger.info("Period processing done")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", base_path="/processing", strict_validation=True, validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8010)
