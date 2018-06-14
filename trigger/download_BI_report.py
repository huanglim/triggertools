# -*- coding: utf-8 -*-
import logging, sys, os

sys.path.append(os.path.dirname(__file__))

from trigger.browserdriver import BrowserDriver
from trigger.processagent import ProcessAgent

from exceptions.exceptions import InvalidCredentials, ReportCriteriaError
from selenium.common.exceptions import NoSuchElementException

# Global Vars
from configs import config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    #filename='app.log',
                    filemode='w'
    )


def download_report(request,
                    dir_name,
                    host=config.IP,
                    port=config.PORT,
                    is_remote=config.IS_REMOTE,
                    username=config.USERNAME,
                    password=config.PASSWORD,
                    url=config.BASE_URL,
                    ):

    #init process agent object
    process_agent = ProcessAgent()

    # generate the selenium functions from the request, the funcion
    # is to be executed in selenium server
    request_functions = process_agent.makeup_functions(request)

    #init the browser driver object
    with BrowserDriver(host=host, port=port, is_remote=is_remote, \
                username=username, password=password, url=url, \
                dirname=dir_name) as driver:

        #loop the functions for  the request and involve browser drvier
        # to run the functions
        for func, value in request_functions.items():
            try:
                process_agent.process_request(driver, func, value)
            except InvalidCredentials as e:
                return False, 'The provided credentials are invalid. \
                    Please type your credentials for authentication.'
            except ReportCriteriaError as e:
                return False, 'The report can not run successfully,\
                    Please double check your input criteria!'
            except NoSuchElementException as e:
                return False, 'The necessary field is invalid, please \
                check your input or your authentication'
            except Exception as e:
                raise

    return True, 'The report run successfully'

if __name__ == '__main__':
    status, msg = download_report()
    print(status, msg)