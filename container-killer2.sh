#!/bin/bash

# Lista de contenedores a detener
containers=(
    "query1_file"
    "query2_file"
    "query3_file"
    "query4_file"
    "query5_file"
    "worker_windows_1"
    "worker_windows_2"
    "worker_windows_3"
    "worker_windows_4"
    "worker_windows_5"
    "worker_linux_1"
    "worker_linux_2"
    "worker_linux_3"
    "worker_linux_4"
    "worker_linux_5"
    "worker_mac_3"
    "worker_mac_3"
    "worker_mac_3"
    "worker_indie_1"
    "worker_indie_2"
    "worker_indie_3"
    "worker_indie_4"
    "worker_indie_5"
    "worker_2010_1"
    "worker_2010_2"
    "worker_2010_3"
    "worker_2010_4"
    "worker_2010_5"
    "worker_review_indie_3"
    "worker_review_validator_5"
    "query1_file"
    "query4_file"
    "worker_review_positive_1"
    "worker_review_english_2"
    "query5_file"
    "worker_review_action_1"
    "worker_review_action_2"
    "worker_review_validator_3"
    "worker_game_validator_4"


)

# Función para seleccionar N elementos únicos aleatorios de un array
select_random_unique() {
    local n=$1
    local -n input_array=$2
    local output_array=()

    local total=${#input_array[@]}

    if (( n > total )); then
        echo "Error: N es mayor que el tamaño de la lista"
        return 1
    fi

    while (( ${#output_array[@]} < n )); do
        local rand_index=$(( RANDOM % total ))
        local candidate="${input_array[rand_index]}"

        # Asegurarse de que el valor no esté ya seleccionado
        if [[ ! " ${output_array[@]} " =~ " ${candidate} " ]]; then
            output_array+=("$candidate")
        fi
    done

    echo "${output_array[@]}"
}

# Bucle infinito
while true; do
    echo "Iniciando una nueva ronda..."

    # Seleccionar 5 contenedores aleatorios
    selected=($(select_random_unique 5 containers))
    echo "Seleccionados para matar: ${selected[@]}"

    # Matar los contenedores seleccionados
    for container in "${selected[@]}"; do
        echo "Killing container: $container"
        docker kill "$container" 2>/dev/null

        if [[ $? -eq 0 ]]; then
            echo "Successfully killed $container"
        else
            echo "Failed to kill $container or it does not exist."
        fi
    done

    # Esperar 5 segundos
    echo "Esperando 5 segundos antes de la próxima ronda..."
    sleep 15
done
