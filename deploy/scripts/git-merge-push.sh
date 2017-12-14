#!/usr/bin/env bash

cd $HOME

echo "Settings up git..."
git config --global user.email "info@wefindx.org"
git config --global user.name "Travis CI"

echo "Clone the repo..."
git clone --quiet https://${GITHUB_API_KEY}@github.com/${TRAVIS_REPO_SLUG} code

echo "Marking current build..."
cd ./code
echo "${TRAVIS_BUILD_NUMBER}" > .buildno
git merge origin/base
git add .buildno
git commit --message "Travis build: ${TRAVIS_BUILD_NUMBER}"

echo "Push to the master..."
git push --quiet origin master
