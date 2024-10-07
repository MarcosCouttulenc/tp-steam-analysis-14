FROM python:3.9.7-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY common/ ./common
COPY middleware/ ./middleware
COPY worker_game_validator /
ENTRYPOINT ["python", "/main.py"]