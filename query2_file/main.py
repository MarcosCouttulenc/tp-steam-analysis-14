from query2_file import QueryTwoFile
from configparser import ConfigParser   
import logging
import os

def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["file_path"] = os.getenv('FILE_PATH', config["DEFAULT"]["FILE_PATH"])
        config_params["result_query_port"] = os.getenv('RESULT_QUERY_PORT', config["DEFAULT"]["RESULT_QUERY_PORT"])
        config_params["listen_backlog"] = os.getenv('LISTEN_BACKLOG', config["DEFAULT"]["LISTEN_BACKLOG"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    config_params = initialize_config()
    queue_name_origin = config_params["queue_name_origin"]
    logging_level = config_params["logging_level"]
    file_path = config_params["file_path"]
    result_query_port = config_params["result_query_port"]
    listen_backlog = config_params["listen_backlog"]
    
    initialize_log(logging_level)
    
    logging.debug(f"action: config | result: success | queue_name_origin: {queue_name_origin} | logging_level: {logging_level}")

    query_two_reducer_worker = QueryTwoFile(queue_name_origin, file_path, int(result_query_port), int(listen_backlog))
    query_two_reducer_worker.start()


def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()