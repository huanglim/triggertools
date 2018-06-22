import logging
import smtplib
from time import sleep
from db import Cloundant_NoSQL_DB
from configs import config
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    #filename='app.log',
                    filemode='w'
    )

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

def trigger_mail():

    logging.info('start func trigger_mail')
    # loop for checking remote
    while True:

        db = Cloundant_NoSQL_DB()
        # get submitted requests from remote database
        try:
            mail_records = db.query_mail_db()
        except Exception as e:
            logging.error(e)
        else:
            # if has submitted request, loop the requests to process them
            if mail_records:
                for record in mail_records:
                    try:
                        logging.info('Process record. for {}'.format(record['confirm_link']))
                        send_mail(record)
                    except Exception as e:
                        logging.error(e)
                    else:
                        try:
                            db.mark_mail_status(record)
                        except Exception as e:
                            logging.error(e)
        finally:
            db.db_disconnect()

        # sleep for seconds
        sleep(120)

if __name__ == "__main__":
    # funcs = [trigger_mail, trigger_request]


    # for func in funcs:
    #     thr = Thread(target=func, args=(db,))
    #     thr.start()

    trigger_mail()