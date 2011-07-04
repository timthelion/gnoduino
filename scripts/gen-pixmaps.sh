#!/bin/sh

for F in `ls pixmaps/*.svg | grep -v gnoduino`
do
        rsvg --format=png --width=25 --height=25 ${F} `echo ${F} | sed -e 's#.svg#.png#'`
done

for F in `ls pixmaps/*.svg | grep gnoduino`
do
	rsvg --format=png --width=48 --height=48 ${F} `echo ${F} | sed -e 's#.svg#.png#'`
done

