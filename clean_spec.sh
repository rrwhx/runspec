#!/bin/bash

set -x

rm -rf result/
rm -rf tmp/
rm -rf config/*cfg.*

rm -rf benchspec/*/*/run/
rm -rf benchspec/*/*/build/
if [ "$1" == "exe" ]; then
    rm -rf benchspec/*/*/exe/
    echo "exe removed"
fi
