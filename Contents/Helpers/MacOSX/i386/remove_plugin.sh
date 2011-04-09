#!/bin/sh

user=`whoami`
target=/Users/$user$1

echo `rm -rf "$target"`

while [ -d "$target" ]; do
sleep 1
done

exit 0