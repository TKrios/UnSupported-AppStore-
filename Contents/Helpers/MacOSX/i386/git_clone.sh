#!/bin/sh

user=`whoami`
target=/Users/$user$1

git clone $2 "$target"

while [ ! -d $target ]; do
sleep 1
done

echo Success!
exit 0