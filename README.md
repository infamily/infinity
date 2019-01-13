# Infinity Project
[![Travis status](https://travis-ci.org/infamily/infinity.svg?branch=base&style=flat)](https://travis-ci.org/infamily/infinity)

- We believe that people should know how technology is built and develop AI safely. That's why Infinity aims to make make it easy for individuals and organisations to understand and share procedural know how.
- We strive for freedom for all beings to own their time. That's why Infinity aims to make it easy for people to work freely on open projects without a need to have a job or a company; aiming to enable everyone to securely live directly in the society by creating, storing and trading digital assets.

Support the mission by running Infinity openly for public cooperation.

Thanks for your cooperation.

## Quick Start

Checkout and do `docker-compose up` locally.

Prefill with data:
```
docker-compose run web bash
python manage.py migrate
python manage.py createsuperuser
 > username: Admin@D3942DCE
 > email: admin@admin.com
 > password: helloinfinity
python manage.py loaddata fixtures/languages.json
python manage.py loaddata fixtures/currencies.json
python manage.py loaddata fixtures/currency_price_snapshots.json fixtures/hour_price_snapshots.json
exit
docker-compose up
```
http://0.0.0.0:8000/admin

**NB:** For local development with the [client](https://github.com/infamily/infinity-reactjs#readme), localhost needs SSL, which is not yet configured. May temporarily consider using something like [ngrok](https://ngrok.com/), i.e., `./ngrok http 80` to provide over SSL for client.

Check out [conveniences](https://gist.github.com/mindey/34fb97b5082d551ccb3bf24602e243ff) for more management commands.

E.g., to run dbshell in app docker, one needs:
```
apt update && apt install -y postgresql-client
python manage.py dbshel
```

## Quick node deployment:

Check [documentation](https://github.com/infamily/infinity/blob/master/docs/devops.md#deploying-a-ci-with-a-single-node).

### Current workflow:

```
git clone git@github.com:infamily/infinity.git
git fetch --all
git checkout base

git checkout -b feature

...

PR: base <- feature
```

(If branching from master breaks builds, ssh to node, and `git remote prune origin`.)

**NB! Do PR to `base` branch. Bot autodeploys to `master`.**

Regarding environment variables, read [here](docs/envars.md), and regarding devops, [here](docs/devops.md).
