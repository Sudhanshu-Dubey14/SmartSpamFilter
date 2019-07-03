# -*- coding: utf-8 -*-

# \file working_model.py
# \brief  Model implementing code
# This code reads mails individually and the classifies them using pre-trained model
# \author Sudhanshu Dubey
# \version    1.0
# \date   25/6/19

import os
import sys
import time

from supporters.features import mail_features
import pickle

name = sys.argv[1]
current = open(name, "r")
curino = os.fstat(current.fileno()).st_ino
while True:
    while True:
        buf = current.read(1024)
        if buf == "":
            break
        mail_file = buf
    try:
        if os.stat(name).st_ino != curino:
            new = open(name, "r")
            current.close()
            current = new
            curino = os.fstat(current.fileno()).st_ino
            continue
    except IOError:
        pass
    time.sleep(1)

features_matrix = mail_features(mail_file)

ml_model = pickle.load(open('spamfilter.sav', 'rb'))
result = ml_model.predict(features_matrix)
if result == 1:
    print(mail_file + " is a spam!!!")
elif result == 0:
    print(mail_file + " is normal mail.")
else:
    print("something went wrong!!")
