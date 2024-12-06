from result_responser import ResultResponser
from configparser import ConfigParser   
import logging
logging.basicConfig(level=logging.CRITICAL)
import os

def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["result_responser_port"] = os.getenv('RESULT_RESPONSER_PORT', config["DEFAULT"]["RESULT_RESPONSER_PORT"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["tmp_file_path"] = os.getenv('TMP_FILE_PATH', config["DEFAULT"]["TMP_FILE_PATH"])
        config_params["listen_backlog"] = os.getenv('LISTEN_BACKLOG', config["DEFAULT"]["LISTEN_BACKLOG"])
        '''
        config_params["query1_file_ip_port"] = os.getenv('QUERY1_FILE_PORT', config["DEFAULT"]["QUERY1_FILE_IP_PORT"])
        config_params["query2_file_ip_port"] = os.getenv('QUERY1_FILE_PORT', config["DEFAULT"]["QUERY2_FILE_IP_PORT"])
        config_params["query3_file_ip_port"] = os.getenv('QUERY1_FILE_PORT', config["DEFAULT"]["QUERY3_FILE_IP_PORT"])
        config_params["query4_file_ip_port"] = os.getenv('QUERY1_FILE_PORT', config["DEFAULT"]["QUERY4_FILE_IP_PORT"])
        config_params["query5_file_ip_port"] = os.getenv('QUERY1_FILE_PORT', config["DEFAULT"]["QUERY5_FILE_IP_PORT"])
        '''

        config_params["query1_file_ip_port"] = os.getenv('QUERY1_FILE_IP_PORT', config["DEFAULT"]["QUERY1_FILE_IP_PORT"])
        config_params["query2_file_ip_port"] = os.getenv('QUERY2_FILE_IP_PORT', config["DEFAULT"]["QUERY2_FILE_IP_PORT"])
        config_params["query3_file_ip_port"] = os.getenv('QUERY3_FILE_IP_PORT', config["DEFAULT"]["QUERY3_FILE_IP_PORT"])
        config_params["query4_file_ip_port"] = os.getenv('QUERY4_FILE_IP_PORT', config["DEFAULT"]["QUERY4_FILE_IP_PORT"])
        config_params["query5_file_ip_port"] = os.getenv('QUERY5_FILE_IP_PORT', config["DEFAULT"]["QUERY5_FILE_IP_PORT"])

        config_params["port_healthchecker"] = os.getenv('PORT_HEALTHCHECKER')
        config_params["ip_healthchecker"] = os.getenv('IP_HEALTHCHECKER')
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
    
    return config_params

def main():
    config_params = initialize_config()
    result_responser_port = config_params["result_responser_port"]
    logging_level = config_params["logging_level"]
    tmp_file_path = config_params["tmp_file_path"]
    listen_backlog = config_params["listen_backlog"]
    query1_file_ip_port = config_params["query1_file_ip_port"]
    query2_file_ip_port = config_params["query2_file_ip_port"]
    query3_file_ip_port = config_params["query3_file_ip_port"]
    query4_file_ip_port = config_params["query4_file_ip_port"]
    query5_file_ip_port = config_params["query5_file_ip_port"]
    port_healthchecker = config_params["port_healthchecker"]
    ip_healthchecker = config_params["ip_healthchecker"]
    
    initialize_log(logging_level)

    logging.critical("\n\n\n RESULT RESPONSER \n\n\n")
    
    logging.debug(f"action: config | result: success | queue_name_origin: {result_responser_port} | logging_level: {logging_level}")

    result_responser = ResultResponser(
        int(result_responser_port), tmp_file_path, int(listen_backlog), query1_file_ip_port, query2_file_ip_port, 
        query3_file_ip_port, query4_file_ip_port, query5_file_ip_port, ip_healthchecker, port_healthchecker)

    logging.critical("\n\n\n RESULT RESPONSER ANTES DE START \n\n\n")
    result_responser.start()


def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if __name__ == "__main__":
    main()