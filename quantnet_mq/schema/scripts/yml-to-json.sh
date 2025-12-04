#!/bin/bash

find . -name "*.yaml" -exec bash -c 'yq "." $1 | sed "s/.yaml#/.json#/g" > ${1%.*}.json' bash {} \;
