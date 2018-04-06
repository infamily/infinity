# Infinity Project
[![Travis status](https://travis-ci.org/infamily/infinity.svg?branch=base&style=flat)](https://travis-ci.org/infamily/infinity)

- We believe that people should know how technology is built and develop AI safely. That's why Infinity makes it easy for individuals and organisations to share procedural know how, openly and publicly.
- We strive for freedom for all beings to own their time. That's why Infinity makes it easy for people to work freely on open projects without a need to have a job or a company; and securely create, store and trade digital assets.

If you want to copy Infinity or run it on your servers, do so by sharing credit and running Infinity openly publicly as well.

Thanks for your cooperation.


## Quick Start

Checkout and do `docker-compose up` locally.

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
