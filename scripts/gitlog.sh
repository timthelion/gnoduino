#!/bin/sh
if test -d ".git"; then
    git log --stat > ChangeLog
    exit 0
else
    echo "No git repository present."
    exit 1
fi

