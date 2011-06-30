#!/bin/sh

for F in pixmaps/*.svg
do
	for S in "22" "24" "32" "48"
	do
		SIZE="$S"x"$S"
		D=$(echo $F | sed -e "s/scalable/$SIZE/g" | sed -e "s/.svg/.png/")
		if [ ! -e $D ]
		then
			inkscape --export-png=$D -w $S -h $S $F
		fi
	done
done
