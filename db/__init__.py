from cloudant.client import Cloudant
from cloudant.database import CloudantDatabase
from cloudant.document import Document
from cloudant.error import CloudantException
import time
from pprint import pprint
from configs import config

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

    def query_db(self, query_status='submitted'):
        self.database = CloudantDatabase(self.client, config.REQUEST_DBNAME)
        selector = {"status":{"$eq":query_status}}
        return self.database.get_query_result(selector)

    def query_mail_db(self, query_status='submitted'):
        self.database = CloudantDatabase(self.client, config.MAIL_DBNAME)
        selector = {"status":{"$eq":query_status}}
        return self.database.get_query_result(selector)

    def mark_status(self, doc, to_status='processed'):
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
    db.query_db()
