archivo_salida=$1
cantidad_windows=$2
cantidad_linux=$3
cantidad_mac=$4
cantidad_juego_indie=$5
cantidad_decada=$6
cantidad_review_indie=$7
cantidad_positiva=$8
cantidad_action=$9
cantidad_ingles=$10
cantidad_reducer_one=$11
cantidad_reducer_two=$12
cantidad_reducer_three=$13
cantidad_reducer_four=$14
cantidad_reducer_five=$15
cantidad_game_validator=$16
cantidad_review_validator=$17

echo "Nombre del archivo de salida: $archivo_salida"
echo "Cantidad de clientes: $cantidad_clientes"

python3 generador-de-compose.py "$archivo_salida" "$cantidad_windows" "$cantidad_linux" "$cantidad_mac" "$cantidad_juego_indie" "$cantidad_decada" "$cantidad_review_indie" "$cantidad_positiva" "$cantidad_action" "$cantidad_ingles" "$cantidad_reducer_one" "$cantidad_reducer_two" "$cantidad_reducer_three" "$cantidad_reducer_four" "$cantidad_reducer_five" "$cantidad_game_validator" "$cantidad_review_validator"
