#!/bin/bash

stardog query $DATABASE "$1"

#| grep -oPe "\s.*?:.*?\s" | awk -F ':' '{print $0}'

