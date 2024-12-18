#!/usr/bin/env python3

from configparser import ConfigParser   
import logging
import os
from client import Client


def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["server_port"] = os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"])
        config_params["server_ip"] = os.getenv('SERVER_IP', config["DEFAULT"]["SERVER_IP"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["result_responser_ip"] = os.getenv('RESULT_RESPONSER_IP', config["DEFAULT"]["RESULT_RESPONSER_IP"])
        config_params["games_file_path"] = os.getenv('GAMES_FILE_PATH')
        config_params["reviews_file_path"] = os.getenv('REVIEWS_FILE_PATH')
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    server_port = config_params["server_port"]
    server_ip = config_params["server_ip"]
    result_responser_ip = config_params["result_responser_ip"]
    games_file_path = config_params["games_file_path"]
    reviews_file_path = config_params["reviews_file_path"]

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | server_port: {server_port} | "
                  f"server_ip: {server_ip} | result_responser_ip: {result_responser_ip} | logging_level: {logging_level}")

    # Initialize server and start server loop

    client = Client(server_ip, server_port, result_responser_ip, games_file_path, reviews_file_path)
    client.start()

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )



if __name__ == "__main__":
    main()
