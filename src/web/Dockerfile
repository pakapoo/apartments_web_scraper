FROM python:latest

WORKDIR /app
COPY . /app
RUN pip install flask mysql-connector-python boto3
EXPOSE 5000

CMD ["python", "./flask/app.py"]