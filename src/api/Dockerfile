FROM python:3.8

WORKDIR /src/api

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python","./api_run.py"]
CMD ["no_config_specified"]
