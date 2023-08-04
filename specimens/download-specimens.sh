#!/bin/bash

while read -r link
do
	dir=$(echo "$link" | cut -d/ -f2- | cut -d/ -f2- | cut -d/ -f2-)
	echo $dir
	mkdir -p $dir
	
	script_link=$link"php/deploy.php"
	image_link=$link"images/logo.png"
	wget --content-disposition -P "$dir" --post-data="request=deployLinux" "$script_link"
	wget -P "$dir" "$image_link"
done < "$1"
