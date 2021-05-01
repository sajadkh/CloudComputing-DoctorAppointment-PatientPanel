FROM python:3.7

ADD . /project

WORKDIR /project

RUN pip install -r requirements.txt
RUN chmod 777 ./start.sh


EXPOSE 8002

CMD ["./start.sh"]
