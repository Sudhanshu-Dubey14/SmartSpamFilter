#! /bin/bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WATCHDIR="$CURDIR/new_mails"
WATCHLOG="$CURDIR/watchlog"

if [ -f $WATCHLOG ]; then
	rm $WATCHLOG
	touch $WATCHLOG
else
	touch $WATCHLOG
fi

pkill inotifywait -r -d $WATCHDIR -o $WATCHLOG --format %w%f -e create -e moved_to
pkill python3 $CURDIR/fast_single.py $WATCHLOG
pkill $0

inotifywait -r -d $WATCHDIR -o $WATCHLOG --format %w%f -e create -e moved_to 
python3 $CURDIR/fast_single.py $WATCHLOG
