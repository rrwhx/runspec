#!/bin/bash
ulimit -s unlimited
ulimit -c unlimited

source shrc

run=runcpu
if [ ! -d "${SPEC}/benchspec/CPU/" ]
then
    relocate
    run=runspec
fi

if test -z $1 ; then
    echo "@1 cfg"
    echo "@2 test,ref,train"
    echo "@3 number of times to run"
    echo "@4: benchmark and others"
    exit
fi

date
set -x
$run -c $1 -i $2 -n $3 "${@:4}"
set +x
date

