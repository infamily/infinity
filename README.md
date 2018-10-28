# Infinity Project
[![Travis status](https://travis-ci.org/infamily/infinity.svg?branch=base&style=flat)](https://travis-ci.org/infamily/infinity)

- We believe that people should know how technology is built and develop AI safely. That's why Infinity aims to make make it easy for individuals and organisations to understand and share procedural know how.
- We strive for freedom for all beings to own their time. That's why Infinity aims to make it easy for people to work freely on open projects without a need to have a job or a company; aiming to enable everyone to securely live directly in the society by creating, storing and trading digital assets.

Support the mission by running Infinity openly for public cooperation.

Thanks for your cooperation.

## Quick Start

Checkout and do `docker-compose up` locally.

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
