# -*- coding: utf-8 -*-

##
# \file spam_filter.py
# \brief  Model building code
# This code builds, trains and tests a new Machine Learning model
# \author Sudhanshu Dubey
# \version    1.0
# \date   25/6/2019
# \bug No known bugs


import os
from supporters.working_model import predict


def multiple(mail_dir):
    ##
    # \brief   Method to predict results for all mails individually
    # \param    mail_dir The directory containing mails
    # \return   Nothing

    i = 0
    emails = [os.path.join(mail_dir, f) for f in os.listdir(mail_dir)]  # reads file names in directory
    with open("result.txt", "w") as res:
        for mail in emails:
            result = predict(mail)
            if result == 1:
                res.write(mail + " is a spam!!!\n")
            elif result == 0:
                res.write(mail + " is normal mail.\n")
            else:
                res.write("something went wrong for " + mail + "\n")
            i = i + 1
            print(i)
            print(mail + " is processesd.")


multiple('a/')
