#!/usr/bin/env python3

from configparser import ConfigParser   
import logging
import os
from worker_review_validator import WorkerReviewValidator

def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
        config_params["queues_name_destiny"] = os.getenv('QUEUES_NAME_DESTINY', config["DEFAULT"]["QUEUES_NAME_DESTINY"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["db_games_ip"] = os.getenv('DB_GAMES_IP', config["DEFAULT"]["DB_GAMES_IP"])
        config_params["db_games_port"] = os.getenv('DB_GAMES_PORT', config["DEFAULT"]["DB_GAMES_PORT"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    config_params = initialize_config()
    queue_name_origin = config_params["queue_name_origin"]
    queues_name_destiny = config_params["queues_name_destiny"]
    logging_level = config_params["logging_level"]
    db_games_ip = config_params["db_games_ip"]
    db_games_port = config_params["db_games_port"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | queue_name_origin: {queue_name_origin} | queues_name_destiny: {queues_name_destiny}" 
                  f"| db_games_ip: {db_games_ip} | db_games_port: {db_games_port} | logging_level: {logging_level}")

    worker_review_validator = WorkerReviewValidator(queue_name_origin, queues_name_destiny, db_games_ip, int(db_games_port))
    worker_review_validator.start()

def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )



if __name__ == "__main__":
    main()