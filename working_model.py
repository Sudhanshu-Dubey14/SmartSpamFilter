# -*- coding: utf-8 -*-

import sys

from supporters.features import mail_features
import numpy as np
import pickle


mail_file = sys.argv[1]
features_matrix = mail_features(mail_file)
np.savetxt("working_matrix.txt", features_matrix)

ml_model = pickle.load(open('spamfilter.sav', 'rb'))
result = ml_model.predict(features_matrix)
if result == 1:
    print(mail_file + " is a spam!!!")
elif result == 0:
    print(mail_file + " is normal mail.")
else:
    print("something went wrong!!")
