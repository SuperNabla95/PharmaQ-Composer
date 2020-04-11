FROM python:3.7
MAINTAINER "3 di Denari"


ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

ADD . /app
ADD test.db /tmp

EXPOSE 5000
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5000"]
#ENTRYPOINT ["flask", "run"]
