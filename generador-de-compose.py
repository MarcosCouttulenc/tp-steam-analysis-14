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
cantidad_linux = 5
cantidad_mac = 5
cantidad_juego_indie = 3
cantidad_decada = 3
cantidad_review_indie = 5
cantidad_positiva = 8
cantidad_action = 5
cantidad_ingles = 15
cantidad_reducer_one = 1
cantidad_reducer_two = 6
cantidad_reducer_three = 3
cantidad_reducer_four = 3
cantidad_reducer_five = 3
cantidad_clientes = 2
cantidad_review_validator = 5 * cantidad_clientes
cantidad_game_validator = 5 * cantidad_clientes
'''
game_files = {"1": "100games.csv", "2": "100games.csv"}
review_files = {"1": "10reviews.csv", "2": "10reviews.csv"}
'''

game_files = {"1": "fullgames.csv", "2": "fullgames2.csv"}
review_files = {"1": "data1porcent.csv", "2": "data0.1porcent.csv"}


#Los puertos de los lideres arrancan en 9000
#port_master = 9000


def generar_compose():
    port_master = 9000
    texto_a_escribir = "name: tp-steam-analysis\n"
    texto_a_escribir += "services:\n"

    # Agregar la configuración del server
    texto_a_escribir += "  server:\n"
    texto_a_escribir += "    container_name: server\n"
    texto_a_escribir += "    image: server:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += f"      - CANT_GAME_VALIDATORS={cantidad_game_validator}\n"
    texto_a_escribir += f"      - CANT_REVIEW_VALIDATORS={cantidad_review_validator}\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    texto_a_escribir += "  result_responser:\n"
    texto_a_escribir += "    container_name: result_responser\n"
    texto_a_escribir += "    image: result_responser:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - server\n\n"

    # Agregar la configuración del cliente
    for i in range(1, cantidad_clientes + 1):
        texto_a_escribir += f"  client_{i}:\n"
        texto_a_escribir += f"    container_name: client_{i}\n"
        texto_a_escribir += "    image: client:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - CLI_ID={i}\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - GAMES_FILE_PATH={game_files[str(i)]}\n"
        texto_a_escribir += f"      - REVIEWS_FILE_PATH={review_files[str(i)]}\n"
        texto_a_escribir += "    volumes:\n"
        texto_a_escribir += "      - ./client/config.ini:/client/config.ini\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - result_responser\n\n"

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
        is_master = (i == 1)
        texto_a_escribir += f"  worker_windows_{i}:\n"
        texto_a_escribir += f"    container_name: worker_windows_{i}\n"
        texto_a_escribir += "    image: worker_windows:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_one}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_windows_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_windows}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_windows_1'}\n\n"

    # Agregar contenedores para worker_linux
    port_master += 1
    for i in range(1, cantidad_linux + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_linux_{i}:\n"
        texto_a_escribir += f"    container_name: worker_linux_{i}\n"
        texto_a_escribir += "    image: worker_linux:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_one}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_linux_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_linux}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_linux_1'}\n\n"

    # Continuar con el resto de los tipos de contenedores basados en las variables recibidas...
    # Ejemplo para `worker_mac`
    port_master += 1
    for i in range(1, cantidad_mac + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_mac_{i}:\n"
        texto_a_escribir += f"    container_name: worker_mac_{i}\n"
        texto_a_escribir += "    image: worker_mac:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_one}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_mac_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_mac}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_mac_1'}\n\n"
    
     # Generar contenedores para worker_indie
    port_master += 1
    for i in range(1, cantidad_juego_indie + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_indie_{i}\n"
        texto_a_escribir += "    image: worker_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_decada}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_indie_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_juego_indie}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_indie_1'}\n\n"
    
     # Generar contenedores para worker_2010
    port_master += 1
    for i in range(1, cantidad_decada + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_2010_{i}:\n"
        texto_a_escribir += f"    container_name: worker_2010_{i}\n"
        texto_a_escribir += "    image: worker_2010:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_two}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_2010_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_decada}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_2010_1'}\n\n"
    
     # Generar contenedores para worker_review_indie
    port_master += 1
    for i in range(1, cantidad_review_indie + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_review_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_indie_{i}\n"
        texto_a_escribir += "    image: worker_review_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_three}\n" 
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_indie_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_review_indie}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_review_indie_1'}\n\n"

    # Generar contenedores para worker_review_positive
    port_master += 1
    for i in range(1, cantidad_positiva + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_review_positive_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_positive_{i}\n"
        texto_a_escribir += "    image: worker_review_positive:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_ingles}\n"        
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_positive_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_positiva}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_review_positive_1'}\n\n"

    # Generar contenedores para worker_review_action
    port_master += 1
    for i in range(1, cantidad_action + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_review_action_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_action_{i}\n"
        texto_a_escribir += "    image: worker_review_action:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_positiva},{cantidad_reducer_five}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_action_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_action}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_review_action_1'}\n\n"

    # Generar contenedores para worker_review_english
    port_master += 1
    for i in range(1, cantidad_ingles + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_review_english_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_english_{i}\n"
        texto_a_escribir += "    image: worker_review_english:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_four}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_english_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_ingles}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'worker_review_english_1'}\n\n"

    # Generar contenedores para query reducers
    port_master += 1
    for i in range(1, cantidad_reducer_one + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  query1_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query1_reducer_{i}\n"
        texto_a_escribir += "    image: query1_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query1_reducer_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_one}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'query1_reducer_1'}\n\n"

    port_master += 1
    for i in range(1, cantidad_reducer_two + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  query2_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query2_reducer_{i}\n"
        texto_a_escribir += "    image: query2_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query2_reducer_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_two}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'query2_reducer_1'}\n\n"

    port_master += 1
    for i in range(1, cantidad_reducer_three + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  query3_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query3_reducer_{i}\n"
        texto_a_escribir += "    image: query3_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query3_reducer_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_three}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'query3_reducer_1'}\n\n"

    port_master += 1
    for i in range(1, cantidad_reducer_four + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  query4_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query4_reducer_{i}\n"
        texto_a_escribir += "    image: query4_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query4_reducer_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_four}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'query4_reducer_1'}\n\n"

    port_master += 1
    for i in range(1, cantidad_reducer_five + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  query5_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query5_reducer_{i}\n"
        texto_a_escribir += "    image: query5_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=query5_reducer_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_reducer_five}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'rabbitmq' if is_master else 'query5_reducer_1'}\n\n"
    
    # generar contenedores para cada query_file
    texto_a_escribir += "  query1_file:\n"
    texto_a_escribir += "    container_name: query1_file\n"
    texto_a_escribir += "    image: query1_file:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    texto_a_escribir += "  query2_file:\n"
    texto_a_escribir += "    container_name: query2_file\n"
    texto_a_escribir += "    image: query2_file:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    texto_a_escribir += "  query3_file:\n"
    texto_a_escribir += "    container_name: query3_file\n"
    texto_a_escribir += "    image: query3_file:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    texto_a_escribir += "  query4_file:\n"
    texto_a_escribir += "    container_name: query4_file\n"
    texto_a_escribir += "    image: query4_file:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    texto_a_escribir += "  query5_file:\n"
    texto_a_escribir += "    container_name: query5_file\n"
    texto_a_escribir += "    image: query5_file:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedor de BDD

    texto_a_escribir += "  database:\n"
    texto_a_escribir += "    container_name: database\n"
    texto_a_escribir += "    image: database:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += f"      - CANT_CLIENTS={cantidad_clientes}\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"


    port_master += 1
    # Generar contenedores para worker_game_validator
    for i in range(1, cantidad_game_validator + 1):
        is_master = (i == 1)

        texto_a_escribir += f"  worker_game_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_game_validator_{i}\n"
        texto_a_escribir += "    image: worker_game_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_mac},{cantidad_windows},{cantidad_linux},{cantidad_juego_indie},1\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_game_validator_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_game_validator}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'database' if is_master else 'worker_game_validator_1'}\n\n"

    # Generar contenedores para worker_review_validator
    port_master += 1
    for i in range(1, cantidad_review_validator + 1):
        is_master = (i == 1)
        texto_a_escribir += f"  worker_review_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_validator_{i}\n"
        texto_a_escribir += "    image: worker_review_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_review_indie},{cantidad_action}\n"
        texto_a_escribir += f"      - IS_MASTER={str(is_master)}\n"
        texto_a_escribir += f"      - PORT_MASTER={port_master}\n"
        texto_a_escribir += f"      - IP_MASTER=worker_review_validator_1\n"
        texto_a_escribir += f"      - CANT_SLAVES={cantidad_review_validator}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += f"      - {'database' if is_master else 'worker_review_validator_1'}\n\n"

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