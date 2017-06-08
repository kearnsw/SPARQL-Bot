#!/bin/bash

./lib/stardog-5.0-beta/bin/stardog-admin db create -n test
./bin/bot $@


