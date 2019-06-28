FROM python:3.6-slim-stretch as bigimage
MAINTAINER Mahyar Abbaspour <mahyar.abaspour@gmail.com>
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev
RUN mkdir -p /app
COPY ./requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

FROM python:3.6-slim-stretch as smallimage
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /app
COPY --from=bigimage /usr/lib /usr/lib
COPY --from=bigimage /lib /lib
COPY --from=bigimage /root/.cache /root/.cache
COPY --from=bigimage /app/requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt && rm -rf /root/.cache
COPY ./rss_reader /app
CMD ["celery", "-A", "rss_reader", "beat", "-l", "info"]
