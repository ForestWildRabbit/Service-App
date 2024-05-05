FROM python:3.10-alpine3.19

WORKDIR /service

EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install --upgrade pip

COPY requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password service-user

USER service-user

COPY service /service