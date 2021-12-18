FROM python:3.8

WORKDIR /

copy ./src/api /home/api/src/api
copy ./config /home/api/src/api/config

RUN pip install -r requirements.txt

ENTRYPOINT ["python","/home/api/src/api/api_run.py"]
CMD ["no_config_specified"]
