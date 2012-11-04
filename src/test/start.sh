#! /bin/sh

# script that starts game server/client and curses gfx client

# start main app -> server+client in background
# store pid to kill later
cd ../main/test
rm *.log
eval '(python3 -B ./testclient.py >../../test/client-err.log 2>&1) &'
TESTCLIENT=$!

# start curses client
cd ../../gfxclient/curses
rm *.log
python3 ./main.py

kill $TESTCLIENT
