from configparser import ConfigParser   
import logging
import os
import logging



class WorkerMain():
    def __init__(self, ClassToInitialize):
        self.ClassToInitialize = ClassToInitialize
    
    def start(self):
        config_params = self.initialize_config()
        queue_name_origin = config_params["queue_name_origin"]
        queues_name_destiny = config_params["queues_name_destiny"]
        logging_level = config_params["logging_level"]
        cant_next = config_params["cant_next"]
        is_master = config_params["is_master"]
        port_master = config_params["port_master"]
        ip_master = config_params["ip_master"]
        queue_name_origin_eof = config_params["queue_name_origin_eof"]
        cant_slaves = config_params["cant_slaves"]
        port_healthchecker = config_params["port_healthchecker"]
        ip_healthchecker = config_params["ip_healthchecker"]
        id = config_params["id"]
        path_status_info = config_params["path_status_info"]

        self.initialize_log(logging_level)
    
        logging.debug(f"action: config | result: success | logging_level: {logging_level}")

        print(f"action: {self.ClassToInitialize.__name__} - start")
        worker = self.ClassToInitialize(
            queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, 
            is_master, ip_master, port_master, ip_healthchecker, port_healthchecker, id, path_status_info
        )
        worker.start()


    def initialize_config(self):
        config = ConfigParser(os.environ)
        # If config.ini does not exists original config object is not modified
        config.read("config.ini")

        config_params = {}
        try:
            config_params["queue_name_origin"] = os.getenv('QUEUE_NAME_ORIGIN', config["DEFAULT"]["QUEUE_NAME_ORIGIN"])
            config_params["queues_name_destiny"] = os.getenv('QUEUES_NAME_DESTINY', config["DEFAULT"]["QUEUES_NAME_DESTINY"])
            config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
            config_params["cant_next"] = os.getenv('CANT_NEXT')
            config_params["is_master"] = os.getenv('IS_MASTER')
            config_params["port_master"] = os.getenv('PORT_MASTER')
            config_params["ip_master"] = os.getenv('IP_MASTER')
            config_params["queue_name_origin_eof"] = os.getenv('QUEUE_NAME_ORIGIN_EOF', config["DEFAULT"]["QUEUE_NAME_ORIGIN_EOF"])
            config_params["cant_slaves"] = os.getenv('CANT_SLAVES')
            config_params["port_healthchecker"] = os.getenv('PORT_HEALTHCHECKER')
            config_params["ip_healthchecker"] = os.getenv('IP_HEALTHCHECKER')
            config_params["id"] = os.getenv('ID')
            config_params["path_status_info"] = os.getenv('PATH_STATUS_INFO', config["DEFAULT"]["PATH_STATUS_INFO"])
            
        except KeyError as e:
            raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
        except ValueError as e:
            raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

        return config_params

    def initialize_log(self, logging_level):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging_level,
            datefmt='%Y-%m-%d %H:%M:%S',
        )