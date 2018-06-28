import logging
import smtplib
import os
from time import sleep
from queue import Queue
from db import Cloundant_NoSQL_DB
from threading import Thread
from trigger.download_BI_report import download_report

from utils.commands import send_to_sftpserver, mkdir

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from configs import config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    #filename='app.log',
                    filemode='w'
    )

class MyRequest(object):

    def __init__(self, request):
        self.request = request
        self.dirname = ''
        self.status = None
        self.msg = ''

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue=None):
        """"""
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            item = self.in_queue.get()
            try:
                result = self.func(item)
            except Exception as e:
                logging.error(e)
            else:
                if not self.out_queue:
                    self.out_queue.put(result)

def get_requests():

    logging.debug('in get requests')
    db = Cloundant_NoSQL_DB()
    try:
        requests = []
        requests_rq = db.query_request_db()
        requests_sc = db.query_schedule_db()
        requests.extend(requests_sc)
        requests.extend(requests_rq)
    except Exception as e:
        logging.error(e)
    else:
        return requests
    finally:
        db.db_disconnect()

def download_request(request):

    logging.info('start func download_request')
    # loop for checking remote

    user = request.request['user']
    request.dirname = mkdir(user)

    #process with the selenium function
    logging.info('Procsss record for user {}'.format(user))
    try:
        request.status, request.msg = download_report(request.request, request.dirname)
        logging.info('The reuslt is {}, msg is {}'.format(request.status, request.msg))
    except Exception as e:
        raise
    else:
        return request

def update_request(request):

    logging.info('in update request')
    db = Cloundant_NoSQL_DB()

    try:
        if request.status:
            if request.request.get('schedule cycle'):
                db.update_schedule_task(request.request)
            else:
                db.mark_request_status(request.request)
    except Exception as e:
        logging.error('the process is failed, status is {}, msg is {}'\
                      .format(request.status, request.msg))
    else:
        return request
    finally:
        db.db_disconnect()

def send_via_mail(request):

    logging.info('sending downloaded file to user mailbox directly')
    msg = MIMEMultipart()
    msg['From'] = config.MAIL_SENDER
    msg['To'] = request.request['user']
    msg['Subject'] = config.MAIL_SUBJECT

    # add MIMEText:
    msg.attach(MIMEText('Hi, Thanks for using Megabot. Please find your report in the attachement',
                        'plain', 'utf-8'))

    # add file:
    dir = os.path.join(config.DEFAULT_DIR, request.request['user'])

    for _, _, files in os.walk(dir):
        for pos, file in enumerate(files):
            with open(os.path.join(dir, file), 'rb') as f:
                mime = MIMEBase('text', 'csv', filename=file)
                mime.add_header('Content-Disposition', 'attachment', filename=file)
                mime.add_header('Content-ID', '<{}>'.format(pos))
                mime.add_header('X-Attachment-Id', '{}'.format(pos))
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
                try:
                    os.remove(os.path.join(dir, file))
                except Exception:
                    logging.error('Error on remove file {}'.format(os.path.join(dir, file)))

    server = smtplib.SMTP(config.MAIL_SERVER)
    # server.set_debuglevel(1)
    server.sendmail(msg['From'], [msg['To']], msg.as_string())
    server.quit()

def send_downloaded_file(request):
    try:
        logging.info('sending the downloaded report to AA server')
        send_to_sftpserver(request)
    except TimeoutError as e:
        logging.error('AA server is not connectable!')
        send_via_mail(request)
    except Exception as e:
        logging.error(e)
        send_via_mail(request)

if __name__ == '__main__':

    # db = Cloundant_NoSQL_DB()
    # for request in get_requests():
    #     request = MyRequest(request)
    #     request.status = True
    #     update_request(request)
    logging.info('Program downloader is started. ')
    get_request_queue = Queue()
    download_request_queue = Queue()
    update_request_queue = Queue()
    # sendmail_queue = Queue()

    threads = [
        Worker(download_request, get_request_queue, download_request_queue),
        Worker(update_request, download_request_queue, update_request_queue),
        Worker(send_downloaded_file, update_request_queue),
    ]

    for thread in threads:
        thread.start()

    while True:
        try:
            requests = get_requests()
        except Exception as e:
            logging.error(e)
        else:
            for r in requests:
                logging.info(r)
                request = MyRequest(r)
                get_request_queue.put(request)

        sleep(300)