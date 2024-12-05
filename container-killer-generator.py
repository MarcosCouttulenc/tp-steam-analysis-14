from random import randint
import subprocess
import time
import random

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
    for i in range(4):
        num = randint(1, 5)
        container_name = random.choice(contaners_name)
        container_to_kill = f"{container_name}_{num}"
        cadena += f"docker kill {container_to_kill}\n"
        
    # for container in contaners_name:
    #     
    #     container_to_kill = f"{container}_{num}"
    #     cadena += f"docker kill {container_to_kill}\n"
    
    # Matar un file al azar
    num = randint(1, 5)
    cadena += f"docker kill query{num}_file\n"

    # Matar un healthchecker al azar
    num = randint(1, 3)
    #cadena += f"docker kill health_checker_{num}\n"

    # Matar la BDD
    cadena += "docker kill database\n"

    with open(archivo_salida, 'w') as file:
        file.write(cadena)

def run_script():
    try:
        result = subprocess.run(
            ['bash', archivo_salida],  # Comando para ejecutar el script
            check=True,             # Levantar una excepción si falla el script
            stdout=subprocess.PIPE, # Captura la salida estándar
            stderr=subprocess.PIPE  # Captura la salida de error
        )
        print("Salida del script:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:", e.stderr.decode())

def main():
    while True:
        generate_script()
        run_script()
        time.sleep(25)
    

main()
