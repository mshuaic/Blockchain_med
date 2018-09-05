#!/bin/bash

if (( $# <= 1 )); then
    echo "feed me some files"
    exit
fi

prefix=test
postfix=.txt

sample=$1
count=0

mkdir $sample

while [ -n "$2" ] && [ -r $2 ]
do
    head -$sample $2 > $sample/$prefix$count$postfix
    ((count++))
    shift
done
