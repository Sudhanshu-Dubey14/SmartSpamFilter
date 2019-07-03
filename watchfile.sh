#! /bin/bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WATCHDIR="$CURDIR/new_mails"
WATCHLOG="$CURDIR/watchlog"

inotifywait -r -d $WATCHDIR -o $WATCHLOG --format %w%f -e create -e moved_to 
python3 $CURDIR/fast_single.py $WATCHLOG
echo "Spam filter started"
