#!/bin/sh

user=`whoami`
target=/Users/$user$1

change_dir=`cd "$target"`
echo $change_dir

download_zip-`curl -o "$2.zip" -L "$3"`
echo $download_zip

expand_archive=`unzip -uo "$2.zip" -d "$target/$2_temp"`
echo $expand_archive

delete_old=`rm -rf $2`
echo $delete_old

rename_temp=`mv -f $2* ./$2`

delete_zip=`rm "$2.zip"`
echo $delete_zip

echo Success!
exit 0