FROM python:3.11

WORKDIR /opt/tests

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH="${PYTHONPATH}:/opt/tests"

COPY . .

ENTRYPOINT ["/entrypoint.sh"]