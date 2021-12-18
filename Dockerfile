FROM python:3.9-slim-buster

RUN apt update
RUN apt install snmpd snmp libsnmp-dev -y

WORKDIR /home/api

copy ./requirements.txt /home/api/requirements.txt
copy ./src/api /home/api/src/api
copy ./config /home/api/src/api/config

RUN pip install -r /home/api/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/api/src"

RUN touch /home/api/config/config.yaml

CMD python3 ./src/api/api_run.py
