#!/bin/bash

# source ESP-IDF env setup script
. "$1"

# remove first argument
shift

# run provided commands
exec "$@"