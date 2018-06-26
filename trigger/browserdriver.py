"""
The module is provide the function to simulate human actions 
for the ILC report download page in the remote selenium server
"""

import logging, os
import functools
import time, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from exceptions.exceptions import InvalidCredentials, ReportCriteriaError

from configs import config

def show_log(func):

    @functools.wraps(func)
    def wrapper(*arg, **kw):
        logging.debug('The section %s is starting' %(func.__name__))
        res = func(*arg, **kw)
        time.sleep(1)
        logging.debug('The section %s is complete'%(func.__name__))
        return res
    return wrapper

class BrowserDriver(object):
    """docstring for NewWebDriver"""
    def __init__(self, driver_type='Chrome', msg='', status = True, \
        host='localhost', port=5555, is_remote=False, username='', \
        password='', url='', dirname=''):

        self.msg = msg
        self.status = status
        self.driver_type = driver_type
        self.host = host
        self.port = port
        self.remote = is_remote
        self.username = username
        self.password = password
        self.url = url
        self.dirname = dirname
        self.account_times = 1

    def __enter__(self):
        if not self.remote:
            if self.driver_type == 'Chrome':
                self.options = webdriver.ChromeOptions()
                #self.options.add_argument('headless')
                #self.options.add_argument('isable-gpu')
                #self.options.add_argument('window-size=1200x600')
                self.prefs = {'profile.default_content_settings.popups': 0, \
                'download.default_directory': os.getcwd()}
                self.options.add_experimental_option('prefs', self.prefs)
                try:
                    self.driver = webdriver.Chrome(chrome_options=self.options)
                except Exception as e:
                    raise
            elif self.driver_type == 'Firefox':
                fp = webdriver.FirefoxProfile()
                fp.set_preference("browser.download.folderList",2)
                fp.set_preference("browser.download.manager.showWhenStarting",False)
                fp.set_preference("browser.download.dir", os.getcwd())
                fp.set_preference("browser.helperApps.neverAsk.saveToDisk", \
                "application/octet-stream")
                try:
                    self.driver = webdriver.Firefox(firefox_profile=fp)
                except Exception as e:
                    raise
            else:
                logging.error('driver type is incorrect!')
                raise ValueError('driver type is incorrect!')
        else:
            if self.driver_type == 'Chrome':
                self.options = webdriver.ChromeOptions()
                #self.options.add_argument('headless')
                #self.options.add_argument('isable-gpu')
                #self.options.add_argument('window-size=1200x600')
                self.prefs = {'profile.default_content_settings.popups': 0, \
                'download.default_directory': self.dirname}
                self.options.add_experimental_option('prefs', self.prefs)
                try:
                    self.driver = webdriver.Remote(''.join(['http://',self.host,':',str(self.port),'/wd/hub']),  
                            #desired_capabilities=DesiredCapabilities.CHROME,
                            desired_capabilities=self.options.to_capabilities()
                            )
                except Exception as e:
                    raise
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        self.driver.quit()

    @show_log
    def logon_check(self, value):

        try:
            self.driver.get(self.url)
            time.sleep(5)
            WebDriverWait(self.driver, config.WAITSEC).until(lambda x: x.find_element_by_xpath("//input[@id='CAMUsername']"))
        except Exception as e:
            raise
        else:
            logging.debug('username is {}, password is {}'.format(self.username, self.password))
            self.driver.find_element_by_xpath("//input[@id='CAMUsername']").clear()
            self.driver.find_element_by_xpath("//input[@id='CAMUsername']").send_keys(self.username)
            self.driver.find_element_by_xpath("//input[@id='CAMPassword']").clear()
            self.driver.find_element_by_xpath("//input[@id='CAMPassword']").send_keys(self.password)
            self.driver.find_element_by_xpath("//input[@id='cmdOK']").click()

        retry_times = 30
        while True and retry_times>0:
            try:
                WebDriverWait(self.driver, 1).until(lambda x:x.find_element_by_xpath\
                    ("//button[starts-with(@name, 'cancel')]"))
            except TimeoutException as e:
                logging.debug('checking the logon status')
            except Exception as e:
                raise
            else:
                break

            try:
                WebDriverWait(self.driver, 1).until(lambda x:x.find_element_by_xpath\
                    ("//*[contains(text(),\"invalid\") or contains(text(),\"RSV-CM-0005\")]"))
            except TimeoutException as e:
                logging.debug('checking the logon status')
            except Exception as e:
                raise
            else:
                logging.error('invalid id or password')
                raise InvalidCredentials

            retry_times -= 1

            if retry_times == 0:
                raise StopIteration

    @show_log
    def sel_rpt_lvl(self, value):

        try:  
            WebDriverWait(self.driver, config.WAITSEC).until(lambda x: x.find_element_by_xpath("//option[@dv='"+value+"']"))
        except TimeoutException as e:
            raise NoSuchElementException
        except Exception as e:
            raise
        else:
            self.driver.find_element_by_xpath("//option[@dv='"+value+"']").click()
        
    @show_log
    def sel_cty_comp(self, value):

        try:
            WebDriverWait(self.driver, config.WAITSEC).until(lambda x: x.find_element_by_xpath("//option[@dv='"+value+"']"))
        except TimeoutException as e:
            raise NoSuchElementException
        except Exception as e:
            raise
        else:
            self.driver.find_element_by_xpath("//option[@dv='"+value+"']").click()
        
    @show_log
    def wk_date_start(self, value):
        if isinstance(value, datetime.datetime):
            start_date_value = '-'.join([str(value.year), str(value.month), str(value.day)])
        else:
            start_date_value = value
        element = self.driver.find_element_by_xpath("//input[@class='clsSelectDateEditBox']")
        element.clear()
        element.send_keys(start_date_value)
    
    @show_log
    def wk_date_end(self, value):
        if isinstance(value, datetime.datetime):
            end_date_value = '-'.join([str(value.year), str(value.month), str(value.day)])
        else:
            end_date_value = value
        element = self.driver.find_elements_by_xpath("//input[@class='clsSelectDateEditBox']")
        element[1].clear()
        element[1].send_keys(end_date_value)
        
    @show_log
    def sel_rpt_format(self, value):
        self.driver.find_element_by_xpath("//option[@dv='"+value+"']").click()

    @show_log
    def sel_rpt_crit(self, value):
        self.driver.find_element_by_xpath("//option[@dv='"+value+"']").click()
        # wait until the input widget come up
        #time.sleep(15)
        #WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//input[@class='clsTextWidget pt']"))

    @show_log
    def sel_acc_emp(self, value):
        if value == 'Account':
            value = 'Account '

        WebDriverWait(self.driver,config.WAITSEC).until(lambda x:x.find_element_by_xpath("//input[@dv='"+value+"']"))
        self.driver.find_element_by_xpath("//input[@dv='"+value+"']").click()
        
    @show_log
    def input_field(self, value):
        self.driver.find_element_by_xpath("//input[@class='clsTextWidget pt']").send_keys(value)

        # calculate times of account
        self.account_times = value.count(',') or value.count(';')

    def enter_acc(self, value):
        return self.input_field(value)

    def enter_dep(self, value):
        return self.input_field(value)

    def enter_sn(self, value):
        return self.input_field(value)

    def enter_workitem(self, value):
        return self.input_field(value)

    @show_log
    def run_report(self, value):
        # if the export botton can not click, raise the exception 
        try:
            self.driver.find_element_by_xpath("//button[starts-with(@name,'finish')]").click()
        except Exception as e:
            logging.error('The report can not run successfully,\
                please double check your input criteria!')
            raise ReportCriteriaError

    @show_log
    def save_image(self, filename=''):
        self.driver.get_screenshot_as_file(self.dirname+'/error.png')

    @show_log
    def export_report(self, value):

        WebDriverWait(self.driver, config.WAITSEC).until(lambda x:x.find_element_by_xpath\
            ("//span[@lid='HLExportReportResult_NS_']"))

        #get current windows handle id
        nowhandle = self.driver.current_window_handle

        #
        self.driver.find_element_by_xpath("//span[@lid='HLExportReportResult_NS_']").click()

        #
        allhandles = self.driver.window_handles
        logging.debug('print all of the handle: %s' %allhandles)

        for handle in allhandles:
            if handle != nowhandle:
                self.driver.switch_to_window(handle)
                WebDriverWait(self.driver, 30).until(lambda x:x.find_element_by_xpath("//td[@class='headerTitle']"))
                logging.info('waiting for download file...')
                if self.account_times >=3:
                    time.sleep(config.WAITSEC*4)