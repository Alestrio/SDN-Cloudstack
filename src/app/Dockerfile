FROM python:3.8

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python","./aplication_run.py"]
CMD ["no_config_specified"]