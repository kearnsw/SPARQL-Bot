#!/bin/bash

echo $1 >> $BOT_HOME/sparql/user_removed.ttl
stardog data remove $DATABASE $BOT_HOME/sparql/user_removed.ttl
rm $BOT_HOME/sparql/user_removed.ttl
