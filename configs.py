import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    IP = '9.110.24.227'
    # IP = '9.112.56.150'
    PORT = 4444
    WAITSEC = 15
    IS_REMOTE = True
    IS_USER_NEEDED = True

    USERNAME = os.environ.get('USER_ID')
    PASSWORD = os.environ.get('USER_PASSWORD')

    INVALID_VALUES = ['n/a', 'none,', 'na', '']
    DEFAULT_DIR = '/dev/shm/'

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'd25ml01.ibm.com')
    MAIL_SENDER = 'apdb2@au.ibm.com'
    MAIL_SUBJECT = 'Megabot report'

    REQUEST_DBNAME = "megabot_request"
    USER_DBNAME = "megabot_user"
    MAIL_DBNAME ='megabot_mail'
    SCHEDULE_DBNAME = 'megabot_schedule'
    DB_USERNAME = '0d0ab079-7631-442d-8355-a466779cb63d-bluemix'
    DB_PASSWORD = '45e643fcad1755a4828ff390196db82cb01d480537d99367cfbeaa3f39acddf5'
    DB_URL = 'https://0d0ab079-7631-442d-8355-a466779cb63d-bluemix:' \
             '45e643fcad1755a4828ff390196db82cb01d480537d99367cfbeaa' \
             '3f39acddf5@0d0ab079-7631-442d-8355-a466779cb63d-bluemix.cloudant.com'

    BASE_URL = 'https://w3-03.ibm.com/transform/bacc/cognos/bi01n/ServletGateway/servlet/' \
    'Gateway?b_action=cognosViewer&ui.action=run&ui.object=%2fcontent%2ffolder%5b' \
    '%40name%3d%27IMG%27%5d%2ffolder%5b%40name%3d%27IMG%20NETEZZA%27%5d%2fpackage%' \
    '5b%40name%3d%27IMG%20All%20Labor%20Package%27%5d%2freport%5b%40name%3d%27GDDM%' \
    '20Various%20Labor%20Reports%27%5d&ui.name=GDDM%20Various%20Labor%20Reports&' \
    'run.outputFormat=&run.prompt=true'

    function_mapping = {
        'Select Report Level': 'sel_rpt_lvl',
        'Select Country/Company': 'sel_cty_comp',
        'Weekending Date Range Start date': 'wk_date_start',
        'Weekending Date Range End date': 'wk_date_end',
        'Select Report Format': 'sel_rpt_format',
        'Select Report Criteria': 'sel_rpt_crit',
        'Account / Employee': 'sel_acc_emp',
        'Input Field': 'input_field',
        'Enter Account ID': 'enter_acc',
        'Enter Department': 'enter_dep',
        'Enter Serial number ': 'enter_sn',
        'Enter workitem': 'enter_workitem'
    }

    function_order = {
        'Select Report Level': 1,
        'Select Country/Company': 2,
        'Weekending Date Range Start date': 3,
        'Weekending Date Range End date': 4,
        'Select Report Format': 5,
        'Select Report Criteria': 6,
        'Account / Employee': 7,
        'Input Field': 9,
        'Enter Account ID': 8,
        'Enter Department': 8,
        'Enter Serial number ': 8,
        'Enter workitem': 8
    }

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass

config_list = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

config = config_list['default']()