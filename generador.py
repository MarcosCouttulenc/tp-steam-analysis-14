import pandas as pd

def sampleten():
    # Cargamos el archivo de datos
    data = pd.read_csv('reviews.csv')
    # Obtenemos el 10% de los datos
    data = data.sample(frac=0.001)
    # Guardamos los datos en un nuevo archivo
    data.to_csv('data0.1porcent.csv', index=False)


def main():
    sampleten()

main()