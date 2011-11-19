#!/bin/bash
set -e
set -x
nosetests --with-doctest --with-id -w src
