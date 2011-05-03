#!/bin/sh

sudo apt-get install python-dev make libtool gcc
./virtenv-bootstrap.py env
make -C pow

