import os
from collections import namedtuple


HOSTNAME = '9.112.57.146'
PORT = 4444
#PARMFILE_NAME = 'dlr.xlsx'
PARMFILE_NAME = 'parameter_template.xlsx'
DEF_SHEET_NAME = 'request'
WAITSEC = 15
IS_REMOTE = True
IS_USER_NEEDED = True

USERNAME = os.environ.get('USER_ID')
PASSWORD = os.environ.get('USER_PASSWORD')

INVALID_VALUES = ['n/a','none,','na', '']

BASE_URL = 'https://w3-03.ibm.com/transform/bacc/cognos/bi01n/ServletGateway/servlet/\
Gateway?b_action=cognosViewer&ui.action=run&ui.object=%2fcontent%2ffolder%5b\
%40name%3d%27IMG%27%5d%2ffolder%5b%40name%3d%27IMG%20NETEZZA%27%5d%2fpackage%\
5b%40name%3d%27IMG%20All%20Labor%20Package%27%5d%2freport%5b%40name%3d%27GDDM%\
20Various%20Labor%20Reports%27%5d&ui.name=GDDM%20Various%20Labor%20Reports&\
run.outputFormat=&run.prompt=true'


function_mapping = {
	'Select Report Level':'sel_rpt_lvl',
	'Select Country/Company':'sel_cty_comp',
	'Weekending Date Range Start date':'wk_date_start',
	'Weekending Date Range End date':'wk_date_end',
	'Select Report Format':'sel_rpt_format',
	'Select Report Criteria':'sel_rpt_crit',
	'Account / Employee':'sel_acc_emp',
	'Input Field':'input_field',
	'Enter Account ID':'enter_acc',
	'Enter Department':'enter_dep',
	'Enter Serial number ':'enter_sn',
	'Enter workitem':'enter_workitem'
}


Request = namedtuple('Request','report_level country_or_company start_date end_date \
          report_format report_criteria report_output_level \
          account_id department serial_number workitem' )