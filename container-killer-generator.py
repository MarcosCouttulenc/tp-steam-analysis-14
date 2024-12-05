from random import randint

contaners_name = [
    "worker_game_validator",
    "worker_linux",
    "worker_windows",
    "worker_mac",
    "worker_indie",
    "worker_2010",
    "worker_review_validator",
    "worker_review_indie",
    "worker_review_positive",
    "worker_review_english",
    "worker_review_action"
]

archivo_salida = "container-killer.sh"

def generate_script():
    cadena = ""
    # Matar uno de cada worker
    for container in contaners_name:
        num = randint(1, 5)
        container_to_kill = f"{container}_{num}"
        cadena += f"docker kill {container_to_kill}\n"
    
    # Matar un file al azar
    num = randint(1, 5)
    cadena += f"docker kill query{num}_file\n"

    # Matar un healthchecker al azar
    num = randint(1, 3)
    cadena += f"docker kill health_checker_{num}\n"

    # Matar la BDD
    cadena += "docker kill database\n"

    with open(archivo_salida, 'w') as file:
        file.write(cadena)

def main():
    generate_script()

main()
