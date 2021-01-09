#!/bin/bash

# Build the static page and post

if [[ ! "${*}" ]]; then
    msg="minor text change"
else
    msg="${*}"
fi

echo "Commiting with message: '${msg}'"

./script/build-site.py source/ docs/
git add . 
git commit -m "${msg}"
git push origin master

git status
