import logging
import smtplib
import os
from time import sleep
from queue import Queue
from utils.mk_dir import mk_dir
from db import Cloundant_NoSQL_DB
from configs import config
from threading import Thread
from trigger.download_BI_report import download_report

from utils.mk_dir import mkdir

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

from configs import config

logging.basicConfig(level=logging.INFO)

class MyRequest(object):

    def __init__(self, request):
        self.request = request
        self.dirname = ''
        self.status = None
        self.msg = ''

def get_requests(db):
    logging.info('in get requests')
    try:
        requests = db.query_db()
    except Exception as e:
        raise
    else:
        return requests

def download_request(request):

    logging.info('start func download_request')
    # loop for checking remote

    user = request.request['user']
    request.dirname = mkdir(user)

    #process with the selenium function
    logging.info('Procsss record for user {}'.format(user))
    try:
        request.status, request.msg = download_report(request.request, request.dirname)
    except Exception as e:
        raise
    else:
        return request

def update_request(request):

    db = Cloundant_NoSQL_DB()
    if request.status:
        db.mark_status(request.request)
        return request
    else:
        # notify user or retry
        logging.error('the process is failed, status is {}, msg is {}'\
                      .format(request.status, request.msg))
        raise Exception

def sendmail(request):

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
                
                os.remove(os.path.join(dir, file))

    server = smtplib.SMTP(config.MAIL_SERVER)
    server.set_debuglevel(1)
    server.sendmail(msg['From'], [msg['To']], msg.as_string())
    server.quit()

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        """"""
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            item = self.in_queue.get()
            result = self.func(item)
            self.out_queue.put(result)

if __name__ == '__main__':

    get_request_queue = Queue()
    download_request_queue = Queue()
    update_request_queue = Queue()
    sendmail_queue = Queue()

    threads = [
        Worker(download_request, get_request_queue, download_request_queue),
        Worker(update_request, download_request_queue, update_request_queue),
        Worker(sendmail, update_request_queue, sendmail_queue),
    ]

    for thread in threads:
        thread.start()

    db = Cloundant_NoSQL_DB()
    while True:
        for r in get_requests(db):
            logging.info(r)
            request = MyRequest(r)
            get_request_queue.put(request)

        sleep(300)