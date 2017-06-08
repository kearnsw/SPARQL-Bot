#!/bin/bash

stardog query --reasoning $DATABASE "$1"

#| grep -oPe "\s.*?:.*?\s" | awk -F ':' '{print $0}'

