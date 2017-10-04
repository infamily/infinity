FROM python:3.5

ENV PYTHONUNBUFFERED 1
ARG requirements_file

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/$requirements_file && rm -rf /requirements

COPY ./compose/django/docker-entrypoint.sh ./compose/django/uwsgi.sh /usr/local/bin/
RUN chmod +x -R /usr/local/bin

COPY . /app

WORKDIR /app

ENTRYPOINT ["docker-entrypoint.sh"]
