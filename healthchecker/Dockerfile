FROM docker:20.10.10-dind

# Instalar Python 3 y pip
RUN apk add --no-cache python3 py3-pip && ln -sf /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common
COPY middleware/ ./middleware
COPY healthchecker /
ENTRYPOINT ["python", "/main.py"]


#Este cambio es para implementar docker in docker dentro del contenedor. El modo privilegido
#da permisos en el kernel para que el contenedor pueda correr contenedores dentro de el.