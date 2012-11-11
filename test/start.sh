#! /bin/sh

# script that starts game server/client and curses gfx client


# TC == test client
DIR_TC="../src/main/test"
BACK_TC="../.."
PY_TC="./testclient.py"

# ME == map editor
DIR_ME="../src/main"
BACK_ME=".."
PY_ME="./mapeditor.py"

# default
DIR=$DIR_TC
BACK=$BACK_TC
PY=$PY_TC

if [ $1 ]; then
    case $1 in
    mapeditor)
        DIR=$DIR_ME
        BACK=$BACK_ME
        PY=$PY_ME
        ;;
    client)
        DIR=$DIR_TC
        BACK=$BACK_TC
        PY=$PY_TC
        ;;
    esac
fi

# start main app -> server+client in background
# store pid to kill later
cd $DIR
rm *.log
eval "python3 $PY $2 $3 $4 $5 &"
TESTCLIENT=$!

# start curses client
cd $BACK/gfxclient/curses
rm *.log
python3 ./main.py

# to be sure
kill -KILL $TESTCLIENT

