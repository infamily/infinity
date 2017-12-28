# Welcome to Infinity

This documentation is part of the Infinity Project at [infinity.family](https://github.com/infamily).


## Project layout

    deploy/            # Automation of deploying a server node with Ansible.
    production.yml     # Docker settings for production.
    docker-compose.yml # Docker settings for local development.
    infty/             # The main django server project with its apps.
    config/            # Main project Django configuration.
    requirements/      # Python requirements, ./local.txt for local development.
    fixtures/          # Initial data needed after initializing server from scratch.
    manage.py          # The main django management command.
    mkdocs.yml         # The documentation configuration file.
    docs/              
        index.md       # The documentation file.

## A note on Project Devops

The [Infinity Server](https://github.com/infamily/infinity#infinity-project) is actually a server software project, and only have CI for testing purposes. It is up for every organization that runs the forks to create its deployments. An organization is recommended to deploy its server using GeoDNS, on a single API. Currently known backbone organizations:

- [test.wfx.io](https://test.wfx.io) (**WeFindX Foundation**, Ireland)
- (none yet) (**GlobalMindShare, NGO**, United States)

For development purposes, some of us personally running:

- [inf.li](https://inf.li) (Singapore)
- [test.wefindx.io](https://test.wefindx.io) (Shanghai)
