import logging
import smtplib
import os
from time import sleep
from utils.mk_dir import mk_dir
from db import Cloundant_NoSQL_DB
from configs import config
from threading import Thread
from trigger.download_BI_report import download_report
from email.mime.text import MIMEText
logging.basicConfig(level=logging.INFO)

def mkdir(user):
    # make up the dirctory in selenium server to store the report for user
    # and return the dirctory name
    dir_name = os.path.join(config.DEFAULT_DIR, user)
    if not os.path.exists(dir_name):
        output = os.popen('mkdir {}'.format(dir_name))
        logging.info('create dir, the result is {}'.format(output))
    return dir_name

def send_mail(record):

    msg = MIMEText(
        'You are receiving an email to confirm the access request for {}. The linke is : \n {}'.format(record['requester'],record['confirm_link'])
    )
    msg['Subject'] = record['subject']
    msg['From'] = record['sender']
    msg['To'] = record['to']

    # Send the message via our own SMTP server.
    s = smtplib.SMTP(config.MAIL_SERVER)
    s.send_message(msg)
    s.quit()

def trigger_request(db):

    logging.info('start func trigger_request')
    # loop for checking remote
    while True:

        # get submitted requests from remote database
        requests = db.query_db()

        # if has submitted request, loop the requests to process them
        if requests:
            for request in requests:
                user = request['user']
                dir_name = mkdir(user)

                #process with the selenium function
                logging.info('Procsss record for user {}'.format(user))
                status, msg = download_report(request, dir_name)

                if status:
                    db.mark_status(request)
                else:
                    # notify user or retry
                    logging.error('the process is failed, status is {}, msg is {}'\
                                  .format(status, msg))
        # sleep for seconds
        sleep(60)

def trigger_mail(db):

    logging.info('start func trigger_mail')
    # loop for checking remote
    while True:
        # get submitted requests from remote database
        try:
            mail_records = db.query_mail_db()
        except Exception as e:
            pass
        else:
            # if has submitted request, loop the requests to process them
            if mail_records:
                for record in mail_records:
                    try:
                        logging.info('Process record. for {}'.format(record['confirm_link']))
                        send_mail(record)
                    except Exception as e:
                        raise
                    else:
                        db.mark_mail_status(record)

        # sleep for seconds
        sleep(60)

if __name__ == "__main__":
    funcs = [trigger_mail, trigger_request]

    db = Cloundant_NoSQL_DB()
    for func in funcs:
        thr = Thread(target=func, args=(db,))
        thr.start()