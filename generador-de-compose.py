import sys

archivo_salida = "docker-compose-dev.yaml"

'''
cantidad_windows = 3
cantidad_linux = 3
cantidad_mac = 3
cantidad_juego_indie = 3
cantidad_decada = 3
cantidad_review_indie = 3
cantidad_positiva = 3
cantidad_action = 3
cantidad_ingles = 3
cantidad_reducer_one = 1
cantidad_reducer_two = 3
cantidad_reducer_three = 3
cantidad_reducer_four = 1
cantidad_reducer_five = 1
cantidad_review_validator = 3
cantidad_clientes = 1
cantidad_game_validator = 3 * cantidad_clientes
'''

cantidad_windows = 5
cantidad_linux =5
cantidad_mac = 5
cantidad_juego_indie = 5
cantidad_decada = 5
cantidad_review_indie = 9
cantidad_positiva = 9
cantidad_action = 9
cantidad_ingles = 13
#cantidad_reducer_one = 1
#cantidad_reducer_two = 2
#cantidad_reducer_three = 2
#cantidad_reducer_four = 2
#cantidad_reducer_five = 2
cantidad_clientes = 1
cantidad_review_validator = 13* cantidad_clientes
cantidad_game_validator = 13 * cantidad_clientes
cantidad_health_checkers = 3
cantidad_query1_file = 5
cantidad_query2_file = 5
cantidad_query3_file = 7
cantidad_query4_file = 7
cantidad_query5_file = 9
cantidad_bdds = 6

RESULT_RESPONSER_PORT_START = 11996
PUERTO_BDD_BASE = 13000

listen_to_result_responser_port = RESULT_RESPONSER_PORT_START
puertos_para_result_responser = {"query1_file": [], "query2_file": [], "query3_file": [], "query4_file": [], "query5_file": []}

for i in range(cantidad_query1_file):
    puertos_para_result_responser["query1_file"].append(str(listen_to_result_responser_port))
    listen_to_result_responser_port += 1

for i in range(cantidad_query2_file):
    puertos_para_result_responser["query2_file"].append(str(listen_to_result_responser_port))
    listen_to_result_responser_port += 1

for i in range(cantidad_query3_file):
    puertos_para_result_responser["query3_file"].append(str(listen_to_result_responser_port))
    listen_to_result_responser_port += 1

for i in range(cantidad_query4_file):
    puertos_para_result_responser["query4_file"].append(str(listen_to_result_responser_port))
    listen_to_result_responser_port += 1

for i in range(cantidad_query5_file):
    puertos_para_result_responser["query5_file"].append(str(listen_to_result_responser_port))
    listen_to_result_responser_port += 1




'''
game_files = {"1": "100games.csv", "2": "1game.csv"}
review_files = {"1": "10reviews.csv", "2": "10reviews.csv"}
'''


game_files = {"1": "fullgames.csv", "2": "1game.csv"}
review_files = {"1": "fullreviews.csv", "2": "10reviews.csv"}



#Los puertos de los lideres arrancan en 9000
#port_master = 9000


def generar_compose():
    port_master = 9000
    texto_a_escribir = "name: tp-steam-analysis\n"
    texto_a_escribir += "services:\n"
    to_healt_checker_number = 0

    # Agregar la configuración del server
    to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
    texto_a_escribir += "  server:\n"
    texto_a_escribir += "    container_name: server\n"
    texto_a_escribir += "    image: server:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += f"      - CANT_GAME_VALIDATORS={cantidad_game_validator - 1}\n"
    texto_a_escribir += f"      - CANT_REVIEW_VALIDATORS={cantidad_review_validator - 1}\n"
    texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
    texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"
    to_healt_checker_number += 1

    for i in range(1, cantidad_health_checkers + 1):
        texto_a_escribir += f"  health_checker_{i}:\n"
        texto_a_escribir += f"    container_name: health_checker_{i}\n"
        texto_a_escribir += "    image: healthchecker:latest\n"
        texto_a_escribir += "    privileged: true\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CONNECT_IP=health_checker_{i + 1 if i < cantidad_health_checkers else 1}\n"
        texto_a_escribir += f"      - CONNECT_PORT=1200{i + 1 if i < cantidad_health_checkers else 1}\n"
        texto_a_escribir += f"      - LISTEN_PORT=1200{i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    volumes:\n"
        texto_a_escribir += "      - /var/run/docker.sock:/var/run/docker.sock\n\n"

    to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
    texto_a_escribir += "  result_responser:\n"
    texto_a_escribir += "    container_name: result_responser\n"
    texto_a_escribir += "    image: result_responser:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
    texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"

    puertos1 = ",".join(puertos_para_result_responser["query1_file"])
    texto_a_escribir += f"      - QUERY1_FILE_IP_PORT=query1_file,{puertos1}\n"

    puertos2 = ",".join(puertos_para_result_responser["query2_file"])
    texto_a_escribir += f"      - QUERY2_FILE_IP_PORT=query2_file,{puertos2}\n"

    puertos3 = ",".join(puertos_para_result_responser["query3_file"])
    texto_a_escribir += f"      - QUERY3_FILE_IP_PORT=query3_file,{puertos3}\n"

    puertos4 = ",".join(puertos_para_result_responser["query4_file"])
    texto_a_escribir += f"      - QUERY4_FILE_IP_PORT=query4_file,{puertos4}\n"

    puertos5 = ",".join(puertos_para_result_responser["query5_file"])
    texto_a_escribir += f"      - QUERY5_FILE_IP_PORT=query5_file,{puertos5}\n"

    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - server\n"
    texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
    to_healt_checker_number += 1


    # Agregar la configuración del cliente
    for i in range(1, cantidad_clientes + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  client_{i}:\n"
        texto_a_escribir += f"    container_name: client_{i}\n"
        texto_a_escribir += "    image: client:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += f"      - CLI_ID={i}\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - GAMES_FILE_PATH={game_files[str(i)]}\n"
        texto_a_escribir += f"      - REVIEWS_FILE_PATH={review_files[str(i)]}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    volumes:\n"
        texto_a_escribir += "      - ./client/config.ini:/client/config.ini\n"
        texto_a_escribir += "      - ./resultados:/resultados\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - result_responser\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Agregar la configuración de RabbitMQ
    texto_a_escribir += "  rabbitmq:\n"
    texto_a_escribir += "    image: rabbitmq:3-management\n"
    texto_a_escribir += "    container_name: rabbitmq\n"
    texto_a_escribir += "    ports:\n"
    texto_a_escribir += "      - \"5672:5672\"\n"
    texto_a_escribir += "      - \"15672:15672\"\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - RABBITMQ_DEFAULT_USER=admin\n"
    texto_a_escribir += "      - RABBITMQ_DEFAULT_PASS=admin\n"
    texto_a_escribir += "      - RABBITMQ_LOG_LEVEL=warning\n"
    texto_a_escribir += "      - RABBITMQ_HEARTBEAT=120\n"
    texto_a_escribir += "    volumes:\n"
    texto_a_escribir += "      - ./middleware/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf\n\n"

    # Generar contenedores para cada tipo según las cantidades
    port_master += 1
    for i in range(1, cantidad_windows + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        is_master = (i == cantidad_windows)
        texto_a_escribir += f"  worker_windows_{i}:\n"
        texto_a_escribir += f"    container_name: worker_windows_{i}\n"
        texto_a_escribir += "    image: worker_windows:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query1_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_windows_{cantidad_windows}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_windows}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_windows_{cantidad_windows}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Agregar contenedores para worker_linux
    port_master += 1
    for i in range(1, cantidad_linux + 1):
        is_master = (i == cantidad_linux)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_linux_{i}:\n"
        texto_a_escribir += f"    container_name: worker_linux_{i}\n"
        texto_a_escribir += "    image: worker_linux:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query1_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_linux_{cantidad_linux}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_linux}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_linux_{cantidad_linux}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Continuar con el resto de los tipos de contenedores basados en las variables recibidas...
    # Ejemplo para `worker_mac`
    port_master += 1
    for i in range(1, cantidad_mac + 1):
        is_master = (i == cantidad_mac)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_mac_{i}:\n"
        texto_a_escribir += f"    container_name: worker_mac_{i}\n"
        texto_a_escribir += "    image: worker_mac:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query1_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_mac_{cantidad_mac}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_mac}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_mac_{cantidad_mac}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
    
     # Generar contenedores para worker_indie
    port_master += 1
    for i in range(1, cantidad_juego_indie + 1):
        is_master = (i == cantidad_juego_indie)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_indie_{i}\n"
        texto_a_escribir += "    image: worker_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_decada - 1}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_indie_{cantidad_juego_indie}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_juego_indie}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_indie_{cantidad_juego_indie}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
    
     # Generar contenedores para worker_2010
    port_master += 1
    for i in range(1, cantidad_decada + 1):
        is_master = (i == cantidad_decada)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_2010_{i}:\n"
        texto_a_escribir += f"    container_name: worker_2010_{i}\n"
        texto_a_escribir += "    image: worker_2010:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query2_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_2010_{cantidad_decada}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_decada}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_2010_{cantidad_decada}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
    
     # Generar contenedores para worker_review_indie
    port_master += 1
    for i in range(1, cantidad_review_indie + 1):
        is_master = (i == cantidad_review_indie)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_review_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_indie_{i}\n"
        texto_a_escribir += "    image: worker_review_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query3_file}\n" 
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_indie_{cantidad_review_indie}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_review_indie}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_review_indie_{cantidad_review_indie}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Generar contenedores para worker_review_positive
    port_master += 1
    for i in range(1, cantidad_positiva + 1):
        is_master = (i == cantidad_positiva)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_review_positive_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_positive_{i}\n"
        texto_a_escribir += "    image: worker_review_positive:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_ingles - 1}\n"        
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_positive_{cantidad_positiva}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_positiva}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_review_positive_{cantidad_positiva}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Generar contenedores para worker_review_action
    port_master += 1
    for i in range(1, cantidad_action + 1):
        is_master = (i == cantidad_action)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_review_action_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_action_{i}\n"
        texto_a_escribir += "    image: worker_review_action:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_positiva - 1},{cantidad_query5_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_action_{cantidad_action}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_action}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_review_action_{cantidad_action}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Generar contenedores para worker_review_english
    port_master += 1
    for i in range(1, cantidad_ingles + 1):
        is_master = (i == cantidad_ingles)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_review_english_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_english_{i}\n"
        texto_a_escribir += "    image: worker_review_english:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_query4_file}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_english_{cantidad_ingles}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_ingles}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'worker_review_english_{cantidad_ingles}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    # Generar contenedores para query reducers
    '''
    port_master += 1
    for i in range(1, cantidad_reducer_one + 1):
        is_master = (i == cantidad_reducer_one)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query1_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query1_reducer_{i}\n"
        texto_a_escribir += "    image: query1_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query1_reducer_{cantidad_reducer_one}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_one}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'query1_reducer_{cantidad_reducer_one}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    port_master += 1
    for i in range(1, cantidad_reducer_two + 1):
        is_master = (i == cantidad_reducer_two)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query2_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query2_reducer_{i}\n"
        texto_a_escribir += "    image: query2_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query2_reducer_{cantidad_reducer_two}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_two}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'query2_reducer_{cantidad_reducer_two}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    port_master += 1
    for i in range(1, cantidad_reducer_three + 1):
        is_master = (i == cantidad_reducer_three)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query3_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query3_reducer_{i}\n"
        texto_a_escribir += "    image: query3_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query3_reducer_{cantidad_reducer_three}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_three}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'query3_reducer_{cantidad_reducer_three}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    port_master += 1
    for i in range(1, cantidad_reducer_four + 1):
        is_master = (i == cantidad_reducer_four)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query4_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query4_reducer_{i}\n"
        texto_a_escribir += "    image: query4_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query4_reducer_{cantidad_reducer_four}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_four}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'query4_reducer_{cantidad_reducer_four}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"

        to_healt_checker_number += 1

    port_master += 1
    for i in range(1, cantidad_reducer_five + 1):
        is_master = (i ==  cantidad_reducer_five)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query5_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query5_reducer_{i}\n"
        texto_a_escribir += "    image: query5_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query5_reducer_{cantidad_reducer_five}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_five}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else f'query5_reducer_{cantidad_reducer_five}'}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
    '''
    
    # generar contenedores para cada query_file
    
    listen_to_result_responser_port = RESULT_RESPONSER_PORT_START
    # generar para query1_file
    for i in range(1, cantidad_query1_file + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query1_file_{i}:\n"
        texto_a_escribir += f"    container_name: query1_file_{i}\n"
        texto_a_escribir += "    image: query1_file:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += f"      - LISTEN_TO_RESULT_RESPONSER_PORT={listen_to_result_responser_port}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        listen_to_result_responser_port += 1
    to_healt_checker_number += 1

    for i in range (1, cantidad_query2_file + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query2_file_{i}:\n"
        texto_a_escribir += f"    container_name: query2_file_{i}\n"
        texto_a_escribir += "    image: query2_file:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - LISTEN_TO_RESULT_RESPONSER_PORT={listen_to_result_responser_port}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
        listen_to_result_responser_port += 1

    for i in range (1, cantidad_query3_file + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query3_file_{i}:\n"
        texto_a_escribir += f"    container_name: query3_file_{i}\n"
        texto_a_escribir += "    image: query3_file:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - LISTEN_TO_RESULT_RESPONSER_PORT={listen_to_result_responser_port}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
        listen_to_result_responser_port += 1

    for i in range(1, cantidad_query4_file + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query4_file_{i}:\n"
        texto_a_escribir += f"    container_name: query4_file_{i}\n"
        texto_a_escribir += "    image: query4_file:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - LISTEN_TO_RESULT_RESPONSER_PORT={listen_to_result_responser_port}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
        listen_to_result_responser_port += 1

    for i in range(1, cantidad_query5_file + 1):
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  query5_file_{i}:\n"
        texto_a_escribir += f"    container_name: query5_file_{i}\n"
        texto_a_escribir += "    image: query5_file:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - LISTEN_TO_RESULT_RESPONSER_PORT={listen_to_result_responser_port}\n"
        texto_a_escribir += f"      - ID={i}\n"
        #texto_a_escribir += "    volumes:\n"
        #texto_a_escribir += "      - ./query5_file/status_worker:/status_worker\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
        listen_to_result_responser_port += 1


    puerto_bdd = PUERTO_BDD_BASE
    # Generar contenedor de BDD
    for i in range(1, cantidad_bdds + 1):

        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  database_{i}:\n"
        texto_a_escribir += f"    container_name: database_{i}\n"
        texto_a_escribir += "    image: database:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_CLIENTS={cantidad_clientes}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += f"      - PORT_REVIEWS={puerto_bdd}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1
        puerto_bdd += 1


    port_master += 1
    # Generar contenedores para worker_game_validator
    for i in range(1, cantidad_game_validator + 1):
        is_master = (i == cantidad_game_validator)

        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_game_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_game_validator_{i}\n"
        texto_a_escribir += "    image: worker_game_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_mac - 1},{cantidad_windows - 1},{cantidad_linux - 1},{cantidad_juego_indie - 1},{cantidad_bdds}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_game_validator_{cantidad_game_validator}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_game_validator}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        
        if is_master:
            for j in range(1, cantidad_bdds + 1):
                texto_a_escribir += f"      - database_{j}\n"
        else:
            texto_a_escribir += f"      - worker_game_validator_{cantidad_game_validator}\n"

        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    puertos_bdd_totales = []
    for i in range(PUERTO_BDD_BASE, PUERTO_BDD_BASE + cantidad_bdds):
        puertos_bdd_totales.append(str(i))
    puertos_bdd_totales_str = ",".join(puertos_bdd_totales)



    # Generar contenedores para worker_review_validator
    port_master += 1
    for i in range(1, cantidad_review_validator + 1):
        is_master = (i == cantidad_review_validator)
        to_healt_checker_number = to_healt_checker_number % cantidad_health_checkers
        texto_a_escribir += f"  worker_review_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_validator_{i}\n"
        texto_a_escribir += "    image: worker_review_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_review_indie - 1},{cantidad_action - 1}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_validator_{cantidad_review_validator}\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_review_validator}\n"
        texto_a_escribir += f"      - IP_HEALTHCHECKER=health_checker_{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - PORT_HEALTHCHECKER=1200{to_healt_checker_number + 1}\n"
        texto_a_escribir += f"      - ID={i}\n"
        texto_a_escribir += f"      - BDD_PORTS={puertos_bdd_totales_str}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"

        if is_master:
            for j in range(1, cantidad_bdds + 1):
                texto_a_escribir += f"      - database_{j}\n"
        else:
            texto_a_escribir += f"      - worker_review_validator_{cantidad_review_validator}\n"
        texto_a_escribir += f"      - health_checker_{to_healt_checker_number + 1}\n\n"
        to_healt_checker_number += 1

    texto_a_escribir += "networks:\n"
    texto_a_escribir += "  testing_net:\n"
    texto_a_escribir += "    ipam:\n"
    texto_a_escribir += "      driver: default\n"
    texto_a_escribir += "      config:\n"
    texto_a_escribir += "        - subnet: 172.25.125.0/24\n\n"

    # Escribir el archivo de salida
    with open(archivo_salida, 'w') as file:
        file.write(texto_a_escribir)



def main():
    generar_compose()


main()