#!/bin/sh

user=`whoami`
target=/Users/$user$1

cd "$target"

curl -o "$2.zip" -L "$3"

unzip "$2.zip"

rm -rf $2

rm -rf "$2.zip"

mv -f *$2* $2

echo Success!
exit 0