FROM python:3.8

WORKDIR /src/api

ENV PYTHONPATH /src

COPY . .

RUN pip install -r requirements.txt

#ENTRYPOINT ["python","./api_run.py"]
CMD ["echo", "hello"]