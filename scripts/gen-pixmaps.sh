#!/bin/sh

for F in `ls pixmaps/*.svg | grep -v gnoduino`
do
    rsvg-convert --format=png --width=25 --height=25 -o `echo ${F} | sed -e 's#.svg#.png#'` ${F}
done

for F in `ls pixmaps/*.svg | grep gnoduino`
do
    rsvg-convert --format=png --width=48 --height=48 -o `echo ${F} | sed -e 's#.svg#.png#'` ${F}
done

