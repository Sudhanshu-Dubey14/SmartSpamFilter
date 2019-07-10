# User Manual for using Smart Spam Filter

## Intro

**Smart Spam Filter** is a Machine Learning code written in python that builds, trains, tests and deploys a spam filter for your mail server. It is designed to as convenient to use as possible, but since it has to work closely with the particular mail server the users need to perform some work themselves.

This software is independent of mail server and can be deployed on any mail server. Though the person who is integrating this software with the mail server should be aware of the directory structure of the mail server, like the location of arrival of new mails and where the spam and ham (non-spam) mails are kept.

This core part of this software is written in python and is thus platform independent. But the assisting scripts are written for Bash shell and thus may not work on some operating systems (like MS Windows). But obviously, with some knowledge, the corresponding scripts for Windows can be made by anyone and it is highly encouraged for someone to make them. ;-)

With this said, let's get on with how to set up this software in your mail server.

## Prerequisites

The following packages are required for us to get going:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (version 3.6 and above)
- [INotifyWait](https://linux.die.net/man/1/inotifywait)
- [PIP3](https://pip.pypa.io/en/stable/) (Pip Installs Package)

You can install the above in Debian-based system using the command:

	sudo apt install git python3 inotify-tools python3-pip

The instructions for other Linux distros can be obtained by replacing ``apt`` with suitable package manager (Like ``yum`` for Fedora-based systems)

Now that we have ``pip3`` with us, we will install the following python packages:

- [SpaCy](https://spacy.io/)
- [Scikit-Learn](https://scikit-learn.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Numpy](https://www.numpy.org/)

You can install these packages using the following command:

	pip3 install spacy sklearn beautifulsoup4 numpy

Now there is one last thing to get, and that is English model of Spacy, which is fetched like this:

	python3 -m spacy download en_core_web_sm

And with this, we are all set to configure our spam filter.
Oh, by the way, it's obvious but you need to have a working mail server installed on your system too (though that is not a requirement).

## Getting the Filter

You can get this filter using git:

	git clone <URL>

## Building the ML Model

The file ``spam_filter.py`` is designed to initially build and train your ML model.

For this, you need a lot (really a whole lot) of emails, both spam and ham (non-spam).
Keep all the ham mails in a directory and all the spam mails in a separate directory. Optionally, you can keep them in the empty directories provided in this project and if you are doing it, don't forget to remove the README.md files from those directories.

The number of mails in both the directories should be sufficiently large but not too large. I have tested with a total of 6017 emails and it has worked brilliantly. Also, it would be helpful if there are almost equal spam and ham mails.

You can also open the spam_filter.py file and modify value of the variable ``dic_size``. This variable holds the number of the words that should be stored in the dictionary. By default, it's set to 3000. A larger dictionary gives more accurate results but takes slightly longer to process. So knowing your system capabilities, you should make a wise decision here.

So, after you have got the mails in the directories, here is what you run:

	python3 spam_filter.py /path/to/ham_mails /path/to/spam_mails

Make sure that the first argument is path of the directory containing ham mails and the second one is of that containing spam.
You can append ``time`` at the starting of the command to get the time it took to build and train the model.
Depending on the number of mails and system specifications, it will take some time to process all the mails and create the dictionary and  ML model.

After the process is complete, you will get two extra files called **dictionary** and **spamfilter.sav**. The dictionary represents the vocabulary of the model and the spamfilter.sav is the actual model. A backup of these files will also be created in the ``backup`` directory should you ever need it. 

So you have successfully created your ML model (Yay!). Be careful to not modify any of the auto-generated files.

## Testing the Model

After you have built the model, you should test it for its accuracy. For that there are a few files:

- ``fast_multiple.py``

This file is meant to process a number of files at a time, and is the recommended way of testing the model. It's simple, you just place all the mails in a single directory and then pass that directory to the code. It is highly recommended to only test ham *or* spam mails at once. This will make it easier for you to analyse the results. Also, the test mails should not be the same as the training mails.
If you have modified the ``dic_size`` while building the model, please modify it here also assigning the same value as before.

You start the test like this:

	python3 fast_multiple.py /path/to/mail/directory

Again, appending ``time`` is a good idea.
This will generate a file called ``fastresult.txt``. This file will contain the judgement of the spam filter for each file in plain english.
After analysing the result (and hopefully being satisfied by it) you can delete fastresult.txt file.

- ``working_model.py``

This file is supposed to test a single mail, but it is **NOT RECOMMENDED** to use this file. This is because its slower and you need to do more work for this.

But if you decide to use it anyway, here is how. First, if you have modified the ``dic_size`` while building the model, go into ``supporters/features.py`` and modify the ``dic_size`` there. Then, just run this file like this:

	python3 working_model.py /path/to/mail/file

It will show you the result on the command line itself.

## Deploying the Model

Now that we are satisfied with the accuracy of the model, let's deploy it for real. For this purpose, there is the script ``watchfile.sh``. But before doing anything, first go into ``fast_single.py`` and modify the ``dic_size`` variable.

Now it's a bit tricky, really. Opening the ``watchfile.sh``, you will find two variables ``WATCHDIR`` and ``WATCHLOG``. You should assign the path of those directories that receive new mails to the ``WATCHDIR`` variable. If there are too many directories, then you could put them in a file and modify the ``inotifywait`` command to watch all the directories that are given in that file. For doing this, refer to the [man page of inotifywait](https://linux.die.net/man/1/inotifywait).

The ``WATCHLOG`` variable contains the path of the file where ``inotifywait`` sends its output and ``fast_single.py`` reads its input. So you should set it accordingly.

After you have appropriately set the paths, run the command:

	setsid bash watchfile.sh

``setsid`` will send the process to background. And now you have successfully set the spam filter to continuously watch for new mails and classify them as they come (Yay!).

## Continuous Training

We have our spam filter up and working. But remember that it's a Machine Learning model and learning is a continuous process. There are bound be emails that our filter will classify incorrectly, be it a spam that the filter call ham or a ham that the filter call spam. To learn from its mistakes, we have ``partial_filter.py`` file and its supporting scripts ``is_ham.sh`` and ``is_spam.sh``.

First, go into ``partial_filter.sh`` and modify ``dic_size`` to match the original model. Then open ``is_spam.sh`` and modify the following variables:

1. DIRNAME: Set to the path of directory where ``fast_single.py`` and ``partial_filter.py`` exist.
1. SPAM_DIR: Set to the path where the mail server stores spam mails.
1. SPAM_TRAIN_DIR: Set it to any directory where you want to store mails for retraining.
1. WATCHLOG: Set it to the complete path of the watchlog file which we created while launching the filter.
1. TRAIN_NO: Set it to the number of mails you want your mail to take for retraining at once. Default is 1000.

Similarly, open ``is_ham.sh`` and modify the following variables:

1. DIRNAME: Set to the path of directory where ``fast_single.py`` and ``partial_filter.py`` exist.
1. HAM_DIR: Set to the path where the mail server stores spam mails.
1. HAM_TRAIN_DIR: Set it to any directory where you want to store mails for retraining.
1. WATCHLOG: Set it to the complete path of the watchlog file which we created while launching the filter.
1. TRAIN_NO: Set it to the number of mails you want your mail to take for retraining at once. Default is 1000.

After that, you have to attach these two scripts so that they are invoked by the mail client you are providing.
Set it so that, when the user reports a mail as spam, the client calls ``is_spam.sh`` and passes the complete path of that mail file to the script.
Similarly, when the user reports that a mail classified as spam is actually ham, the client should call ``is_ham.sh`` and pass the complete path of the mail file to the script.

***Congratulations!!!***

You have successfully built, trained, configured and deployed the **Smart Spam Filter**.
Now you can go have some chocolates, well done.
