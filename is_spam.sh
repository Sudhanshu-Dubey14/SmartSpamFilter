#! /bin/bash

SPAMMAIL=$1		# Location of spam mail given by user
SPAM_FILE_NAME="${SPAMMAIL##*/}"
MAIL_DIR="${SPAMMAIL%/*}"
DIRNAME="${MAIL_DIR%/*}"
SPAM_DIR="$DIRNAME/spam"
SPAM_TRAIN_DIR="$DIRNAME/train_spam"
WATCHLOG="$DIRNAME/watchlog"
TRAIN_NO=1000
if [ -d "$SPAM_TRAIN_DIR" ]; then
  if [ ! -L "$SPAM_TRAIN_DIR" ]; then
	  cp $SPAMMAIL $SPAM_TRAIN_DIR
  fi
else
	mkdir $SPAM_TRAIN_DIR
	cp $SPAMMAIL $SPAM_TRAIN_DIR
fi
if [ -d "$SPAM_DIR" ]; then		# Check if spam directory exists or not
  if [ ! -L "$SPAM_DIR" ]; then	# Check if its not a symlink
	  mv $SPAMMAIL $SPAM_DIR
  fi
else
	mkdir $SPAM_DIR
	mv $SPAMMAIL $SPAM_DIR
	echo "$SPAMMAIL is moved"
fi
SPAM_NO="$(ls $SPAM_TRAIN_DIR | wc -l)"	# Count no of files in SPAM_TRAIN_DIR
if [ $SPAM_NO -ge $TRAIN_NO ]; then
	echo "Retraining time... running python code"
	python3 $DIRNAME/partial_filter.py $SPAM_TRAIN_DIR 1
	rm -rf $SPAM_TRAIN_DIR
	PYTHON_PID="$(ps -fu $USER| grep "fast_single.py" | grep -v "grep" | awk '{print $2}')"
	if [ ! -z $PYTHON_PID ];then
		kill $PYTHON_PID
	fi
		setsid python3 $DIRNAME/fast_single.py $WATCHLOG
		echo "Spam filter restarted."	

fi
