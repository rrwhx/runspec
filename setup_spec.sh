#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 config_file" >&2
  exit 1
fi

source shrc

spec=""

run=runcpu
if [ -d "${SPEC}/benchspec/CINT2000/" ]
then
    spec="2000"
elif [ -d "${SPEC}/benchspec/CPU2006/" ]
then
    spec="2006"
elif [ -d "${SPEC}/benchspec/CPU/" ]
then
    spec="2017"
else

    echo "not an SPEC CPU diectory"
    exit 1
fi

echo $spec

if [[ "$spec" == "2000" ]]
then
    ./run.sh $1 test  1 all
    ./run.sh $1 train 1 all
    ./run.sh $1 ref   1 all
elif [[ "$spec" == "2006" ]]
then
    ./run.sh $1 test  1 all -a setup
    ./run.sh $1 train 1 all -a setup
    ./run.sh $1 ref   1 all -a setup
elif [[ "$spec" == "2017" ]]
then
    ./run.sh $1 test  1 -T base -a setup specrate
    ./run.sh $1 train 1 -T base -a setup specrate
    ./run.sh $1 ref   1 -T base -a setup specrate
fi

rm -rf result/
rm -rf tmp/
rm -rf config/*cfg.*

#rm -rf benchspec/*/*/run/
rm -rf benchspec/*/*/build/

