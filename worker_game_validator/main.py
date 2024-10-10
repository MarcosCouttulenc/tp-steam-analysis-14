#!/usr/bin/env python3

from configparser import ConfigParser   
import logging
import os
from worker_game_validator import WorkerGameValidator

def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
        config_params["queues_name_destiny"] = os.getenv('QUEUES_NAME_DESTINY', config["DEFAULT"]["QUEUES_NAME_DESTINY"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["cant_windows"] = os.getenv('CANT_WINDOWS')
        config_params["cant_linux"] = os.getenv('CANT_LINUX')
        config_params["cant_mac"] = os.getenv('CANT_MAC')
        config_params["cant_indie"] = os.getenv('CANT_INDIE')
        config
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
    cant_windows = config_params["cant_windows"]
    cant_linux = config_params["cant_linux"]
    cant_mac = config_params["cant_mac"]
    cant_indie = config_params["cant_indie"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | queue_name_origin: {queue_name_origin} | queues_name_destiny: {queues_name_destiny}" 
                  f"| logging_level: {logging_level}")

    worker_game_validator = WorkerGameValidator(queue_name_origin, queues_name_destiny, cant_windows, cant_linux, cant_mac, cant_indie)
    worker_game_validator.start()

def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )



if __name__ == "__main__":
    main()