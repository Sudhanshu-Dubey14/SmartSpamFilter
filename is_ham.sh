#! /bin/bash

HAMMAIL=$1		# Location of ham mail given by user
HAM_FILE_NAME="${HAMMAIL##*/}"
MAIL_DIR="${HAMMAIL%/*}"
DIRNAME="${MAIL_DIR%/*}"
HAM_DIR="$DIRNAME/ham"
HAM_TRAIN_DIR="$DIRNAME/train_ham"
if [ -d "$HAM_TRAIN_DIR" ]; then
  if [ ! -L "$HAM_TRAIN_DIR" ]; then
	  cp $HAMMAIL $HAM_TRAIN_DIR
  fi
else
	mkdir $HAM_TRAIN_DIR
	cp $HAMMAIL $HAM_TRAIN_DIR
fi
if [ -d "$HAM_DIR" ]; then		# Check if ham directory exists or not
  if [ ! -L "$HAM_DIR" ]; then	# Check if its not a symlink
	  mv $HAMMAIL $HAM_DIR
	  echo "$HAMMAIL is moved"
  fi
else
	mkdir $HAM_DIR
	mv $HAMMAIL $HAM_DIR
	echo "$HAMMAIL is moved"
fi
HAM_NO="$(ls $HAM_TRAIN_DIR | wc -l)"	# Count no of files in HAM_TRAIN_DIR
if [ $HAM_NO -ge 1000 ]; then
	echo "Retraining time... running python code"
	python3 $DIRNAME/partial_filter.py $HAM_TRAIN_DIR 0
	rm -rf $HAM_TRAIN_DIR
fi
