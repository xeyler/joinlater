#!/bin/bash

for archive in "$@"
do
	OUTPUT="$(dirname "$archive")/SecureW2.cloudconfig.xml"

	tmpdir=$(mktemp -d)
	echo "Decompressing archive into $tmpdir"
	sed '0,/^#ARCHIVE#$/d' "$archive" |  gzip -d | tar x -C $tmpdir

	if [[ ! -f "$tmpdir/SecureW2.cloudconfig" ]]; then
		echo "No `SecureW2.cloudconfig` file  found!"
		exit 1
	fi

	openssl smime -verify -inform der -noverify -in "$tmpdir/SecureW2.cloudconfig" -out "$OUTPUT"
done
