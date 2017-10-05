#!/usr/bin/env bash
ansible-playbook -vv -i deploy/ansible/inventories/staging deploy/ansible/site.yml
