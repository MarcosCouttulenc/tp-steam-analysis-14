FROM python:3.9.7-slim
COPY common/ ./common
COPY client /
RUN python -m unittest tests/test_common.py
ENTRYPOINT ["python", "/main.py"]

