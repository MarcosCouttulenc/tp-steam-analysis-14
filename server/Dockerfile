FROM python:3.9.7-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY common/ ./common
COPY middleware/ ./middleware
COPY server /
RUN python -m unittest tests/test_common.py
ENTRYPOINT ["python", "/main.py"]
