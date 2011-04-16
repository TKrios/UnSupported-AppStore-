#!/bin/sh

user=`whoami`
target=/Users/$user$1

#echo $target
#echo "bundle: $2"
#echo "zipPath: $3"

change_dir=`cd "$target"`
echo $change_dir

download_zip-`curl -o "$2.zip" -L "$3"`
echo $download_zip

expand_replace=`unzip -uo "$2.zip" -d "$target/$2"`
echo $expand_replace

delete_zip=`rm "$2.zip"`
echo $delete_zip

#cd "$target"
#curl -o "$2.zip" -L $3
#unzip -uo "$2.zip" -d "$target/$2"
#rm -rf __serverfoldername__
#mv -f __zipfoldername__* ./__serverfoldername__
#rm "$2.zip"

echo Success!
exit 0
