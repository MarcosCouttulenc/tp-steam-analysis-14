from query2_reducer import QueryTwoReducer
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
        config_params["queues_name_destiny"] = os.getenv('QUEUE_NAME_DESTINY', config["DEFAULT"]["QUEUE_NAME_DESTINY"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["is_master"] = os.getenv('IS_MASTER')
        config_params["port_master"] = os.getenv('PORT_MASTER')
        config_params["ip_master"] = os.getenv('IP_MASTER')
        config_params["queue_name_origin_eof"] = os.getenv('QUEUE_NAME_ORIGIN_EOF', config["DEFAULT"]["QUEUE_NAME_ORIGIN_EOF"])
        config_params["cant_slaves"] = os.getenv('CANT_SLAVES')
        config_params["port_healthchecker"] = os.getenv('PORT_HEALTHCHECKER')
        config_params["ip_healthchecker"] = os.getenv('IP_HEALTHCHECKER')

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
    is_master = config_params["is_master"]
    port_master = config_params["port_master"]
    ip_master = config_params["ip_master"]
    queue_name_origin_eof = config_params["queue_name_origin_eof"]
    cant_slaves = config_params["cant_slaves"]
    port_healthchecker = config_params["port_healthchecker"]
    ip_healthchecker = config_params["ip_healthchecker"]
    
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | queue_name_origin: {queue_name_origin} | logging_level: {logging_level}")

    query_two_reducer_worker = QueryTwoReducer(queue_name_origin_eof, queue_name_origin,queues_name_destiny, cant_slaves, is_master, ip_master, port_master, ip_healthchecker, port_healthchecker)
    query_two_reducer_worker.start()


def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()