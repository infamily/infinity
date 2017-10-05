#!/usr/bin/env bash
echo "Run ansible playbook..."
ansible-playbook -vvvv -i deploy/ansible/inventories/staging deploy/ansible/site.yml
