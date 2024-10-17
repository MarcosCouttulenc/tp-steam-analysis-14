import sys

archivo_salida = "docker-compose-dev.yaml"
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
cantidad_reducer_two = 5
cantidad_reducer_three = 6
cantidad_reducer_four = 1
cantidad_reducer_five = 1
cantidad_game_validator = 8
cantidad_review_validator = 9



def generar_compose():
    
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
    texto_a_escribir += "  client:\n"
    texto_a_escribir += "    container_name: client\n"
    texto_a_escribir += "    image: client:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - CLI_ID=1\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
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
    texto_a_escribir += "    volumes:\n"
    texto_a_escribir += "      - ./middleware/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf\n\n"

    # Generar contenedores para cada tipo según las cantidades
    for i in range(1, cantidad_windows + 1):
        texto_a_escribir += f"  worker_windows_{i}:\n"
        texto_a_escribir += f"    container_name: worker_windows_{i}\n"
        texto_a_escribir += "    image: worker_windows:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Agregar contenedores para worker_linux
    for i in range(1, cantidad_linux + 1):
        texto_a_escribir += f"  worker_linux_{i}:\n"
        texto_a_escribir += f"    container_name: worker_linux_{i}\n"
        texto_a_escribir += "    image: worker_linux:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Continuar con el resto de los tipos de contenedores basados en las variables recibidas...
    # Ejemplo para `worker_mac`
    for i in range(1, cantidad_mac + 1):
        texto_a_escribir += f"  worker_mac_{i}:\n"
        texto_a_escribir += f"    container_name: worker_mac_{i}\n"
        texto_a_escribir += "    image: worker_mac:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"
    
     # Generar contenedores para worker_indie
    for i in range(1, cantidad_juego_indie + 1):
        texto_a_escribir += f"  worker_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_indie_{i}\n"
        texto_a_escribir += "    image: worker_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_2010={cantidad_decada}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"
    
     # Generar contenedores para worker_2010
    for i in range(1, cantidad_decada + 1):
        texto_a_escribir += f"  worker_2010_{i}:\n"
        texto_a_escribir += f"    container_name: worker_2010_{i}\n"
        texto_a_escribir += "    image: worker_2010:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_QUERY2_REDUCER={cantidad_reducer_two}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"
    
     # Generar contenedores para worker_review_indie
    for i in range(1, cantidad_review_indie + 1):
        texto_a_escribir += f"  worker_review_indie_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_indie_{i}\n"
        texto_a_escribir += "    image: worker_review_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_QUERY3_REDUCER={cantidad_reducer_three}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_positive
    for i in range(1, cantidad_positiva + 1):
        texto_a_escribir += f"  worker_review_positive_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_positive_{i}\n"
        texto_a_escribir += "    image: worker_review_positive:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        #texto_a_escribir += f"      - CANT_REVIEW_ENGLISH={cantidad_ingles}\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_ingles}\n"        
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_action
    for i in range(1, cantidad_action + 1):
        texto_a_escribir += f"  worker_review_action_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_action_{i}\n"
        texto_a_escribir += "    image: worker_review_action:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        #texto_a_escribir += f"      - CANT_REVIEW_POSITIVE={cantidad_positiva}\n"
        #texto_a_escribir += f"      - CANT_QUERY5_REDUCER={cantidad_reducer_five}\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_positiva},{cantidad_reducer_five}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_english
    for i in range(1, cantidad_ingles + 1):
        texto_a_escribir += f"  worker_review_english_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_english_{i}\n"
        texto_a_escribir += "    image: worker_review_english:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        #texto_a_escribir += f"      - CANT_QUERY4_REDUCER={cantidad_reducer_four}\n"
        texto_a_escribir += f"      - CANT_NEXT={cantidad_reducer_four}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para query reducers
    for i in range(1, cantidad_reducer_one + 1):
        texto_a_escribir += f"  query1_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query1_reducer_{i}\n"
        texto_a_escribir += "    image: query1_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    for i in range(1, cantidad_reducer_two + 1):
        texto_a_escribir += f"  query2_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query2_reducer_{i}\n"
        texto_a_escribir += "    image: query2_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    for i in range(1, cantidad_reducer_three + 1):
        texto_a_escribir += f"  query3_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query3_reducer_{i}\n"
        texto_a_escribir += "    image: query3_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    for i in range(1, cantidad_reducer_four + 1):
        texto_a_escribir += f"  query4_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query4_reducer_{i}\n"
        texto_a_escribir += "    image: query4_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    for i in range(1, cantidad_reducer_five + 1):
        texto_a_escribir += f"  query5_reducer_{i}:\n"
        texto_a_escribir += f"    container_name: query5_reducer_{i}\n"
        texto_a_escribir += "    image: query5_reducer:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"
    
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
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n"
    texto_a_escribir += "    depends_on:\n"
    texto_a_escribir += "      - rabbitmq\n\n"


    # Generar contenedores para worker_game_validator
    for i in range(1, cantidad_game_validator + 1):
        texto_a_escribir += f"  worker_game_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_game_validator_{i}\n"
        texto_a_escribir += "    image: worker_game_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_WINDOWS={cantidad_windows}\n"
        texto_a_escribir += f"      - CANT_LINUX={cantidad_linux}\n"
        texto_a_escribir += f"      - CANT_MAC={cantidad_mac}\n"
        texto_a_escribir += f"      - CANT_INDIE={cantidad_juego_indie}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - database\n\n"

    # Generar contenedores para worker_review_validator
    for i in range(1, cantidad_review_validator + 1):
        texto_a_escribir += f"  worker_review_validator_{i}:\n"
        texto_a_escribir += f"    container_name: worker_review_validator_{i}\n"
        texto_a_escribir += "    image: worker_review_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += f"      - CANT_REV_INDIE={cantidad_review_indie}\n"
        texto_a_escribir += f"      - CANT_REV_ACTION={cantidad_action}\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - database\n\n"

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