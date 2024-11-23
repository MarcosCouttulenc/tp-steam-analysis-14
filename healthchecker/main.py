from healthchecker import HealthChecker
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
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["listen_port"] = os.getenv('LISTEN_PORT')
        config_params["connect_port"] = os.getenv('CONNECT_PORT')
        config_params["connect_ip"] = os.getenv('CONNECT_IP')
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    listen_port = config_params["listen_port"]
    connect_port = config_params["connect_port"]
    connect_ip = config_params["connect_ip"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | logging_level: {logging_level}")

    healthchecker = HealthChecker(listen_port, connect_port, connect_ip)
    healthchecker.start()


def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()