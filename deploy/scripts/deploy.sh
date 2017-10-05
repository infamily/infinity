#!/usr/bin/env bash
ENVIRONMENT=$1
PRIVATE_KEY="~/.ssh/${ENVIRONMENT}"

echo "Run ansible playbook for ${ENVIRONMENT} using private key: ${PRIVATE_KEY}..."
ansible-playbook -vvvv -i deploy/ansible/inventories/staging deploy/ansible/site.yml --private-key=${PRIVATE_KEY}
