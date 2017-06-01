#!/bin/bash

stardog query REVERB "$1" | grep -oPe "\s.*?:.*?\s" | awk -F ':' '{print $2}'

