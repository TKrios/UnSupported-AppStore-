#!/bin/sh

user=`whoami`
target=/Users/$user$1
git='/.git'

if [ ! -d "$target$git" ]; then
    git init $target
    else
    echo '.git found'
fi

{
cd "$target"
echo `git pull $2`
wait $!
}
exit 0