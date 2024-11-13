FROM python:3.10 AS base

WORKDIR /code

FROM base AS build

COPY requirements.txt /

RUN pip install -r /requirements.txt --no-cache-dir \
    && apt-get update \
    && apt-get install netcat-openbsd


COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh


FROM build AS app

COPY . /code

ENTRYPOINT ["/entrypoint.sh"]