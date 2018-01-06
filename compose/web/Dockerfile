FROM python:3.5

ENV PYTHONUNBUFFERED 1
ARG requirements_file

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/$requirements_file && rm -rf /requirements

COPY ./compose/web/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x -R /usr/local/bin

COPY ./compose/web/start-dev.sh /start-dev.sh
RUN sed -i 's/\r//' /start-dev.sh
RUN chmod +x /start-dev.sh

WORKDIR /app

ENTRYPOINT ["docker-entrypoint.sh"]
