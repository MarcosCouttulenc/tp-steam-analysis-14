FROM python:3.9.7-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY common/ ./common
COPY result_responser /
ENTRYPOINT ["python", "/main.py"]