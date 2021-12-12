FROM python:3.9

WORKDIR /api

copy . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python","./api.py"]
CMD ["no_config_specified"]
