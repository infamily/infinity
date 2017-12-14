#!/usr/bin/env bash
PRIVATE_KEY=$1
PRIVATE_KEY_PATH="~/.ssh/${PRIVATE_KEY}"

echo ${VAULT_PASSWORD_KEY} | gpg --passphrase-fd 0 .vault_password.txt.gpg

echo "Push docker image to the Docker Hub..."
docker login -u="${DOCKER_USERNAME}" -p="${DOCKER_PASSWORD}"
docker push infamily/infinity-django:latest

echo "Run ansible playbook using private key: ${PRIVATE_KEY_PATH}..."
ansible-playbook -vv -i deploy/ansible/inventories/staging deploy/ansible/site.yml --private-key=${PRIVATE_KEY_PATH}
