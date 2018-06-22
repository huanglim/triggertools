from cloudant.client import Cloudant
from cloudant.database import CloudantDatabase
from cloudant.document import Document
from cloudant.error import CloudantException
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from configs import config
import logging

class Cloundant_NoSQL_DB(object):
    def __init__(self):
        self.client = Cloudant(config.DB_USERNAME,
                               config.DB_PASSWORD,
                               url=config.DB_URL)
        self.client.connect()


    def write_to_db(self,document,user=None):
        self.database = CloudantDatabase(self.client, config.REQUEST_DBNAME)
        append_info = {"user": user, "ctime": time.ctime()}
        new_document = document.copy()
        new_document.update(append_info)
        if self.database.exists():
            self.database.create_document(new_document)

    def query_request_db(self, query_status='submitted'):
        self.database = CloudantDatabase(self.client, config.REQUEST_DBNAME)
        selector = {"status":{"$eq":query_status}}
        return self.database.get_query_result(selector)


    def query_schedule_db(self, query_status='active'):
        self.database = CloudantDatabase(self.client, config.SCHEDULE_DBNAME)
        today = datetime.now().strftime('%Y-%m-%d')
        selector = {
            "status":{"$eq":query_status},
            "run date":{"$lte":today}
        }
        return self.database.get_query_result(selector)

    def query_mail_db(self, query_status='submitted'):
        self.database = CloudantDatabase(self.client, config.MAIL_DBNAME)
        selector = {"status":{"$eq":query_status}}
        return self.database.get_query_result(selector)

    def mark_request_status(self, doc, to_status='processed'):
        self.database = CloudantDatabase(self.client, config.REQUEST_DBNAME)
        remote_doc = Document(self.database, doc['_id'])
        remote_doc.update_field(
            action=remote_doc.field_set,
            field='status',
            value=to_status
        )
        remote_doc.update_field(
            # action=remote_doc.list_field_append,
            action=remote_doc.field_set,
            field='process time',
            value=time.ctime()
        )

    def mark_schedule_status(self, doc, to_status='disable'):
        self.database = CloudantDatabase(self.client, config.REQUEST_DBNAME)
        remote_doc = Document(self.database, doc['_id'])
        remote_doc.update_field(
            action=remote_doc.field_set,
            field='status',
            value=to_status
        )

    def update_schedule_task(self, doc):
        self.database = CloudantDatabase(self.client, config.SCHEDULE_DBNAME)
        remote_doc = Document(self.database, doc['_id'])
        logging.info(remote_doc)
        old_start_date = datetime.strptime(doc['Weekending Date Range Start date'],'%Y-%m-%d')
        old_end_date = datetime.strptime(doc['Weekending Date Range End date'],'%Y-%m-%d')

        if doc['schedule cycle'] == 'weekly':
            new_start_date = old_start_date + relativedelta(weeks=1)
            new_end_date = old_end_date + relativedelta(weeks=1)
            new_run_date = datetime.today() + relativedelta(weeks=1)
        elif doc['schedule cycle'] == 'monthly':
            new_start_date = old_start_date + relativedelta(months=1)
            new_end_date = old_end_date + relativedelta(months=1)
            new_run_date = datetime.today() + relativedelta(months=1)
        #
        # remote_doc.field_set(remote_doc,
        #                      'Weekending Date Range Start date',
        #                      new_start_date.strftime('%Y-%m-%d')
        #                      )
        #
        # remote_doc.field_set(remote_doc,
        #                      'Weekending Date Range End date',
        #                      new_end_date.strftime('%Y-%m-%d')
        #                      )
        #
        # remote_doc.field_set(remote_doc,
        #                      'run date',
        #                      new_run_date.strftime('%Y-%m-%d')
        #                      )

        remote_doc.update_field(
            action=remote_doc.field_set,
            field='Weekending Date Range Start date',
            value=new_start_date.strftime('%Y-%m-%d')
        )

        remote_doc.update_field(
            action=remote_doc.field_set,
            field='Weekending Date Range End date',
            value=new_end_date.strftime('%Y-%m-%d')
        )

        remote_doc.update_field(
            action=remote_doc.field_set,
            field='run date',
            value=new_run_date.strftime('%Y-%m-%d')
        )

        remote_doc.update_field(
            action=remote_doc.field_set,
            field='last run date',
            value=datetime.today().strftime('%Y-%m-%d')
        )

    def mark_mail_status(self, doc, to_status='processed'):
        self.database = CloudantDatabase(self.client, config.MAIL_DBNAME)
        remote_doc = Document(self.database, doc['_id'])
        remote_doc.update_field(
            action=remote_doc.field_set,
            field='status',
            value=to_status
        )
        remote_doc.update_field(
            # action=remote_doc.list_field_append,
            action=remote_doc.field_set,
            field='process time',
            value=time.ctime()
        )

    def db_disconnect(self):
        self.client.disconnect()

if __name__ == '__main__':
    db = Cloundant_NoSQL_DB()
    db.query_request_db()
