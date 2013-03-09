#! /bin/sh

# this script runs start.sh in xterm with 8x8 or 16x16 fonts

XTERM=xterm
OPTS="-fg white -bg black -geometry 100x100"

# FONT=c64
FONT=c64d

# generate fonts
cd fonts
xset +fp `pwd`
xset fp rehash
cd ..

$XTERM $OPTS -font $FONT ./start.sh
