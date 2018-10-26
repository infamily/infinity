# Infinity Project
[![Travis status](https://travis-ci.org/infamily/infinity.svg?branch=base&style=flat)](https://travis-ci.org/infamily/infinity)

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
