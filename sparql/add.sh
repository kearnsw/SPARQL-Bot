#!/bin/bash

echo $1 >> $BOT_HOME/sparql/user_added.ttl
stardog data add $DATABASE $BOT_HOME/sparql/user_added.ttl

