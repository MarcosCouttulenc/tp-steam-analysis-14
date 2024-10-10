import sys

def generar_compose(archivo_salida, cantidad_windows, cantidad_linux, cantidad_mac, cantidad_juego_indie, cantidad_decada, 
                    cantidad_review_indie, cantidad_positiva, cantidad_action, cantidad_ingles, cantidad_reducer_one, 
                    cantidad_reducer_two, cantidad_reducer_three, cantidad_reducer_four, cantidad_reducer_five, 
                    cantidad_game_validator, cantidad_review_validator):
    
    texto_a_escribir = "name: tp-steam-analysis\n"
    texto_a_escribir += "services:\n"

    # Agregar la configuración del server
    texto_a_escribir += "  server:\n"
    texto_a_escribir += "    container_name: server\n"
    texto_a_escribir += "    image: server:latest\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
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
        texto_a_escribir += f"   container_name: worker_windows_{i}\n"
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
        texto_a_escribir += f"   container_name: worker_linux_{i}\n"
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
        texto_a_escribir += f"   container_name: worker_mac_{i}\n"
        texto_a_escribir += "    image: worker_mac:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"
    
     # Generar contenedores para worker_review_indie
    for i in range(1, cantidad_review_indie + 1):
        texto_a_escribir += f"  worker_review_indie_{i}:\n"
        texto_a_escribir += f"   container_name: worker_review_indie_{i}\n"
        texto_a_escribir += "    image: worker_review_indie:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_positive
    for i in range(1, cantidad_positiva + 1):
        texto_a_escribir += f"  worker_review_positive_{i}:\n"
        texto_a_escribir += f"   container_name: worker_review_positive_{i}\n"
        texto_a_escribir += "    image: worker_review_positive:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_action
    for i in range(1, cantidad_action + 1):
        texto_a_escribir += f"  worker_review_action_{i}:\n"
        texto_a_escribir += f"   container_name: worker_review_action_{i}\n"
        texto_a_escribir += "    image: worker_review_action:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para worker_review_english
    for i in range(1, cantidad_ingles + 1):
        texto_a_escribir += f"  worker_review_english_{i}:\n"
        texto_a_escribir += f"   container_name: worker_review_english_{i}\n"
        texto_a_escribir += "    image: worker_review_english:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - rabbitmq\n\n"

    # Generar contenedores para query reducers
    for i in range(1, cantidad_reducer_one + 1):
        texto_a_escribir += f"  query1_reducer_{i}:\n"
        texto_a_escribir += f"   container_name: query1_reducer_{i}\n"
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
        texto_a_escribir += f"   container_name: query2_reducer_{i}\n"
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
        texto_a_escribir += f"   container_name: query3_reducer_{i}\n"
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
        texto_a_escribir += f"   container_name: query4_reducer_{i}\n"
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
        texto_a_escribir += f"   container_name: query5_reducer_{i}\n"
        texto_a_escribir += "    image: query5_reducer:latest\n"
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
        texto_a_escribir += f"   container_name: worker_game_validator_{i}\n"
        texto_a_escribir += "    image: worker_game_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"

    # Generar contenedores para worker_game_validator
    for i in range(1, cantidad_review_validator + 1):
        texto_a_escribir += f"  worker_review_validator_{i}:\n"
        texto_a_escribir += f"   container_name: worker_review_validator_{i}\n"
        texto_a_escribir += "    image: worker_review_validator:latest\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
        texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
        texto_a_escribir += "    networks:\n"

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
    archivo_salida = sys.argv[1]
    cantidad_de_clientes = sys.argv[2]
    generar_compose(archivo_salida, cantidad_de_clientes)


main()