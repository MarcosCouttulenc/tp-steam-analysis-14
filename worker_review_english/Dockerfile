FROM python:3.9.7-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
#RUN pip install -r english_requirements.txt
COPY common/ ./common
COPY middleware/ ./middleware
COPY worker_review_english /
ENTRYPOINT ["python", "/main.py"]