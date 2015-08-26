#!/bin/bash

epstopdf --outfile=$1.pdf $1.eps

gs \
 -sOutputFile=$1_bw.pdf \
 -sDEVICE=pdfwrite \
 -sColorConversionStrategy=Gray \
 -dProcessColorModel=/DeviceGray \
 -dCompatibilityLevel=1.4 \
 -dNOPAUSE \
 -dBATCH \
 $1.pdf

pdftops -eps $1_bw.pdf

rm $1.pdf
rm $1_bw.pdf
