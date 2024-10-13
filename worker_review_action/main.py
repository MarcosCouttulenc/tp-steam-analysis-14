from worker_review_action import ActionWorker
from configparser import ConfigParser   
import logging
import os
import logging

def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
        config_params["queues_name_destiny"] = os.getenv('QUEUES_NAME_DESTINY', config["DEFAULT"]["QUEUES_NAME_DESTINY"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["cant_query5_reducer"] = os.getenv('CANT_QUERY5_REDUCER')
        config_params["cant_positivas"] = os.getenv('CANT_REVIEW_POSITIVE')   
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
    cant_query5_reducer = config_params["cant_query5_reducer"]
    cant_positivas = config_params["cant_positivas"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | queue_name_origin: {queue_name_origin} | queues_name_destiny: {queues_name_destiny}" 
                  f"| logging_level: {logging_level}")

    print("action: ACTIONWorker - start")
    macos_worker = ActionWorker(queue_name_origin, queues_name_destiny, int(cant_query5_reducer), int(cant_positivas))
    macos_worker.start()


def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()