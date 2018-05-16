import logging

from time import sleep
from utils.mk_dir import mk_dir
from db import Cloundant_NoSQL_DB
from configs import config
from trigger.download_BI_report import download_report

logging.basicConfig(level=logging.INFO)

def mkdir(user, ip):
    # make up the dirctory in selenium server to store the report for user
    # and return the dirctory name
    try:
        dir_name = mk_dir(user, ip)
    except Exception as e:
        logging.error('error occurred in the make dir %s' %e)
        raise
    return dir_name


def main():

    db = Cloundant_NoSQL_DB()

    # loop for checking remote
    while True:

        # get submitted requests from remote database
        requests = db.query_db()

        # if has submitted request, loop the requests to process them
        if requests:
            for request in requests:
                user = request['user']
                dir_name = mkdir(user, config.IP)

                #process with the selenium function
                status, msg = download_report(request, dir_name)

                if status:
                    db.mark_status(request)
                else:
                    # notify user or retry
                    logging.error('the process is failed, status is {}, msg is {}'\
                                  .format(status, msg))

        # sleep for seconds
        sleep(10)

if __name__ == "__main__":
    main()