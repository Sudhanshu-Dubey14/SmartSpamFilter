import os
from supporters.working_model import predict


def multiple(mail_dir):
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
