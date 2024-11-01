from middleware.queue import ServiceQueues
from database  import DataBase
from databaseworker import DataBaseWorker
from configparser import ConfigParser   
import logging
import os

CHANNEL_NAME =  "rabbitmq"


def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["result_query_port"] = os.getenv('RESULT_QUERY_PORT', config["DEFAULT"]["RESULT_QUERY_PORT"])
        config_params["listen_backlog"] = os.getenv('LISTEN_BACKLOG', config["DEFAULT"]["LISTEN_BACKLOG"])
        config_params["cant_clients"] = os.getenv('CANT_CLIENTS')
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    config_params = initialize_config()
    queue_name_origin = config_params["queue_name_origin"]
    logging_level = config_params["logging_level"]
    result_query_port = config_params["result_query_port"]
    listen_backlog = config_params["listen_backlog"]
    cant_clients = config_params["cant_clients"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success ")

    data_base =  DataBase()
    data_base_worker = DataBaseWorker(queue_name_origin, data_base,int(result_query_port), int(listen_backlog), int(cant_clients))
    data_base_worker.start()



def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()