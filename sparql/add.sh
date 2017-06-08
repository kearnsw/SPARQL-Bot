#!/bin/bash
echo "prefix reverbDB: <reverbDB:>" > $BOT_HOME/sparql/user_added.ttl
echo $1 >> $BOT_HOME/sparql/user_added.ttl
stardog data add $DATABASE $BOT_HOME/sparql/user_added.ttl
rm $BOT_HOME/sparql/user_added.ttl

