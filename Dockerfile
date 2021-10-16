FROM python:3.8

WORKDIR /api

copy . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python","./api.py"]
CMD ["no_config_specified"]
