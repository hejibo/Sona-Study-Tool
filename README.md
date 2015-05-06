# Sona Study Tool
[Sona](http://sona-systems.com/) is a cloud-based tool researchers use to manage and recruit research study participants. Some universities assign bonus marks based on participation in studies. This program will detect when there are new study slots and notify user(s) via Gmail. The email will contain a list of the new studies with signup links. It will also attempt to register the user for one of the available study time slots.

#Installation and Setup
##1. Required Python Libraries
This program uses [`requests`](http://docs.python-requests.org/) and [`BeautifulSoup4`](http://www.crummy.com/software/BeautifulSoup/), which can be installed with the following command:

```bash
$ pip install -r requirements.txt
```

##2. Setup
Modify the values in [`data.py`](data.py) with a Gmail login, a Sona login, and at least one email for the email notifications.

The program can be modified to run on other instances of Sona by changing `domain` in [`main.py`](main.py).

##3. Cron Job
Since each execution of the program only checks for studies at that moment of time, use a job scheduler (like Cron) to run the program at regular intervals. You can also log the output by piping the output. For example in Cron,

```
* * * * * cd [location of program] && python main.py 2>> error.log 1>> logging.log
```