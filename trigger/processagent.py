
from collections import Mapping, OrderedDict
import logging
from configs import config

from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ProcessAgent(object):
    """docstring for ProcessRequest"""
    def __init__(self):
        pass
        
    def process_request(self, driver, function, value=''):
        """ 
        The function to process request via selenium server 
        drvier is the object of browserdriver which has the function to manipulate 
        action in selenium server 
        """
        
        is_retry = True
        retry_times = 1
        while is_retry and retry_times>0:
            try:
                getattr(driver, function)(value)
            except TimeoutException as e:
                retry_times -= 1
            # except NoSuchElementException as e:
            #     logging.error('there is no such element for the user \
            #         criteria, please double check for function %s'\
            #         % function)
            #     break
            except Exception as e:
                #driver.save_image()
                raise
            else:
                is_retry = False

    @staticmethod
    def make_function_order(key):
        return config.function_order.get(key) if config.function_order.get(key) else 99
            
    def makeup_functions(self, request):
        if not isinstance(request, Mapping):
            logging.error('the request type should be dict')
            raise AttributeError('the request type should be dict')

        functions = OrderedDict()

        functions['logon_check'] = ''

        order_function = sorted(request, key=ProcessAgent.make_function_order)

        for key in order_function:
            if request[key].lower().strip() not in config.INVALID_VALUES \
                    and request[key] is not None \
                    and config.function_mapping.get(key):
                logging.debug('{}, {}'.format(config.function_mapping.get(key), request[key]))
                functions[config.function_mapping[key]] = request[key]

        # for key, val in request.items():
        #     if str(val).lower().strip() not in config.INVALID_VALUES \
        #             and val is not None \
        #             and config.function_mapping.get(key):
        #         logging.debug(config.function_mapping.get(key))
        #         functions[config.function_mapping[key]] = val

        functions['run_report'] = 5
        functions['export_report'] = ''

        return functions