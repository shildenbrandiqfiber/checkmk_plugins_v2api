#!/bin/bash

MESG=$1

git add -A .

git commit -am "$MESG"

git push -u origin master
