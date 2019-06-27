# -*- coding: utf-8 -*-

"""
@brief  Model implementing code
@detail This code reads mails individually and the classifies them using pre-trained model
@author Sudhanshu Dubey
@version    1.0
@date   25/6/19

"""
import sys

from supporters.features import mail_features
import pickle


mail_file = sys.argv[1]
features_matrix = mail_features(mail_file)

ml_model = pickle.load(open('spamfilter.sav', 'rb'))
result = ml_model.predict(features_matrix)
if result == 1:
    print(mail_file + " is a spam!!!")
elif result == 0:
    print(mail_file + " is normal mail.")
else:
    print("something went wrong!!")
