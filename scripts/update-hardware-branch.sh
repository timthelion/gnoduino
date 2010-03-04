#!/bin/bash

git svn fetch hardware

git checkout hardware-git
git merge hardware-svn
git push origin HEAD

git checkout master
cd hardware
git pull origin hardware-git
cd ..
git add hardware
git commit -m 'update hardware submodule'
