#!/bin/sh

user=`whoami`
target=/Users/$user$1


if [ ! -d $target ]; then
    echo True
else
    echo False
fi
exit 0