# # An example of embedding CEF browser in a PyQt4 application.
# # Tested with PyQt 4.10.3 (Qt 4.8.5).

from datetime import *
import base64
import json
import os, sys, subprocess
import psycopg2, psycopg2.extras
from License import Generator as GetLicense
from structlog import get_logger

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

dbname = 'restaurant'
con = None
project_dir_name="app"

logger =  get_logger(__name__)


class Database:
    def __init__(self):
        self.con = None
        self.dbhost = '127.0.0.1'
        self.dbname = 'restaurant'
        self.dbuser = 'restaurant'
        self.dbpassword = 'restaurant'
        self.project_dir_name = 'app'

    def processconfiguration(self):
        try:
            config_file_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..', 'config','config.json'))
            with open(config_file_path) as data_file:    
                data = json.load(data_file)
                database_data= data["database"]
                self.dbhost = database_data["dbhost"]
                self.dbname = database_data["dbname"]
                self.dbuser = database_data["dbuser"]
                self.dbpassword = database_data["dbpassword"]
        except Exception as ex:
            logger.error('Failed Reading Config', exception=ex)
            self.close_application('Failed Reading Config')

    def connect_postgres(self):
        logger.info('Initializing default postgres database connection')
        self.con = psycopg2.connect(dbname='postgres',user='postgres', host='127.0.0.1',password='root')
        self.con.autocommit = True
        return self.con

    def connect_database(self):
        logger.info('Initializing local database connection')
        con_statement = "dbname='"+str(self.dbname)+"' user='"+str(self.dbuser)+"' host='"+str(self.dbhost)+"' password='"+str(self.dbpassword)+"'"
        self.con = psycopg2.connect(con_statement)
        self.con.autocommit = True
        return self.con

    def close_connection(self):
        self.con.close()

    def create_resources(self):
        try:
            con = self.connect_postgres()
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("select * from pg_database where datname = %(dname)s", {'dname': self.dbname })
            answer = cur.fetchall()
            if len(answer) > 0:
                logger.info("Database {} exists".format(self.dbname))
                cur.execute("DROP DATABASE {}".format(self.dbname))
                cur.execute("DROP ROLE IF EXISTS {}".format(self.dbuser))
                self.create_database_resources(cur, con)
            else:
                logger.info("Database {} does NOT exist".format(self.dbname))
                self.create_database_resources(cur, con)
        except Exception, ex:
            logger.error('Error creating new Database and Role, System exiting ..', exception=ex)
            self.close_application('Error creating new Database.')
        finally:
            if con:
                con.close()

    def create_database_resources(self, cur, con):
        try:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname= %(dbuser)s", {'dbuser': self.dbuser })
            if len(cur.fetchall()) == 0:
                logger.info('Role {} dropped.'.format(self.dbuser))
                # cur.execute("DROP ROLE IF EXISTS {}".format(self.dbuser))
                cur.execute("CREATE ROLE {} WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '{}'".format(self.dbuser, self.dbpassword))

            # cur.execute("CREATE ROLE {} WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '{}'".format(self.dbuser, self.dbpassword))
            cur.execute('CREATE DATABASE {} OWNER {};'.format(self.dbname, self.dbuser))
            con.close()
            conn = self.connect_database()
            cur2 =conn.cursor()
            cur2.execute('CREATE EXTENSION {};'.format('hstore'))
            cur2.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
            conn.commit()
            conn.close()
            logger.info('successful database creation')
            self.generate_license_and_migrate()
        except Exception as  ex:
            logger.error('Error creating role, database and hstore extension', exception=ex)
            
    def format_machine(self, new_id):
        formatted = str(new_id)
        bb = base64.b64encode(bytes(formatted))
        bkey322 = bb.ljust(32)[:32]
        return bkey322

    def windows(self):
        try:
            machine_id = subprocess.check_output('wmic csproduct get UUID').split('\n')[1].strip()
            machine_model_number = subprocess.check_output('wmic csproduct get IdentifyingNumber').split('\n')[1].strip()
            new_id = '{0}@/{1}*'.format(machine_id, machine_model_number)
            mid = self.format_machine(new_id)
            return mid
        except Exception as ex:
            logger.error('Error getting the unique machine id on os platform', exception=ex)

    def generate_license(self):
        try:
            mac = self.windows()
            end_date = (datetime.today() + timedelta(days=30)).date().isoformat()
            gl = GetLicense(mac, end_date)
            return gl.license()
        except Exception as ex:
            logger.error('Error generating license', exception=ex)

    def generate_license_and_migrate(self):
        try:
            keyfiles = self.generate_license()
            keyfile, check = keyfiles.split('###')
            keyfile = keyfile.replace('\r', '').replace('\n', '')
            check = check.replace('\r', '').replace('\n', '')

            try:
                subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','makemigrations'], shell=True)
                subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','migrate',], shell=True)
            except Exception as ex:
                logger.error('Could not makemigrations or migrate', exception=ex)

            conn2 = self.connect_database()
            cur3 = conn2.cursor()
            if self.dbname == 'restaurant':
                logger.info('Insert table data with more columns', dbname=self.dbname)
                cur3.execute("""INSERT INTO userprofile_user(name, email, is_superuser, is_active, is_staff, is_new_code, password, image, send_mail, date_joined, code, rest_code) values('admin', 'admin@example.com', True, True, True, True, 'pbkdf2_sha256$30000$28uVy3qLTKlJ$npN/SiLkufzhREcOyYQFmWmzh1s/ZIo5qXk9/qSWSmE=','', True, now(), '0000', 'admin')""")
            else:
                logger.info('Insert table data', dbname=self.dbname)
                cur3.execute("""INSERT INTO userprofile_user(name, email, is_superuser, is_active, is_staff, password, image, send_mail, date_joined) values('admin', 'admin@example.com', True, True, True, 'pbkdf2_sha256$30000$28uVy3qLTKlJ$npN/SiLkufzhREcOyYQFmWmzh1s/ZIo5qXk9/qSWSmE=','', True, now())""")   
            cur3.execute("""INSERT INTO site_files(file, "check", created, modified) values('"""+keyfile+"""', '"""+check+"""', now(), now())""")
            conn2.commit()
            conn2.close()
            logger.info('Successful license generation')
        except Exception as ex:
            logger.error('Error finalizing the license generation and migrations', exception=ex)

    def close_application(self, message=None):
        text = "Could not start the Application."
        if message:
            text = text + " \n\n" + message
        choice = QtGui.QMessageBox.critical(None, 'Error!',
                                            text,
                                            QtGui.QMessageBox.Ok)
        # exit the system
        sys.exit()
            