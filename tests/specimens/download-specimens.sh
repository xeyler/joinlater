#!/bin/bash

while read -r link
do
	dir=$(echo "$link" | cut -d/ -f4-)
	echo $dir
	mkdir -p $dir
	
	script_link="${link}php/deploy.php"
	image_link="${link}images/logo.png"
	cloud_config_link="${link}linux/SecureW2.cloudconfig"
	wget --content-disposition -P "$dir" --post-data="request=deployLinux" "$script_link"
	wget -P "$dir" "$image_link"
	wget -P "$dir" "$cloud_config_link"
done < "$1"
