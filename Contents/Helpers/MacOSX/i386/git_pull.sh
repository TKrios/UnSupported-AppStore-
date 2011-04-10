#!/bin/sh

user=`whoami`
target=/Users/$user$1
git='/.git'

if [ ! -d "$target$git" ]; then
    echo `git init "$target"`
    wait $!
    echo 'git repo initialized'
    else
    echo '.git found'
fi

{
cd "$target"
echo `git pull $2`
wait $!
}
exit 0