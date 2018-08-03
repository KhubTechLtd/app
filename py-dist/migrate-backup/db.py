# # An example of embedding CEF browser in a PyQt4 application.
# # Tested with PyQt 4.10.3 (Qt 4.8.5).

from datetime import *
import base64
import json
import os, sys, subprocess
import psycopg2, psycopg2.extras
from License import Generator as GetLicense

dbname = 'restaurant'
con = None
project_dir_name="app"


class Database:
    def __init__(self):
        self.con = None
        self.dbhost = '127.0.0.1'
        self.dbname = 'restaurant'
        self.dbuser = 'restaurant'
        self.dbpassword = 'restaurant'
        self.project_dir_name = 'app'

    def processconfiguration(self):
        config_file_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..', 'config','config.json'))
        try:
            with open(config_file_path) as data_file:    
                data = json.load(data_file)
                database_data= data["database"]
                self.dbhost = database_data["dbhost"]
                self.dbname = database_data["dbname"]
                self.dbuser = database_data["dbuser"]
                self.dbpassword = database_data["dbpassword"]
        except Exception as e:
            print (e)
            print ("Failed Reading Config")

    def connect_postgres(self):
        self.con = psycopg2.connect(dbname='postgres',user='postgres', host='127.0.0.1',password='root')
        self.con.autocommit = True
        return self.con

    def connect_database(self):
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
                print "Database {} exists".format(self.dbname)
                cur.execute("DROP DATABASE {}".format(self.dbname))
                cur.execute("DROP ROLE {}".format(self.dbuser))
                self.create_database_resources(cur, con)
            else:
                print "Database {} does NOT exist".format(self.dbname)
                self.create_database_resources(cur, con)
        except Exception, e:
            print "Error %s" %e
            sys.exit(1)
        finally:
            if con:
                con.close()

    def create_database_resources(self, cur, con):
        try:
            cur.execute("CREATE ROLE {} WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '{}'".format(self.dbuser, self.dbpassword))
            cur.execute('CREATE DATABASE {} OWNER {};'.format(self.dbname, self.dbuser))
            con.close()
            conn = self.connect_database()
            cur2 =conn.cursor()
            cur2.execute('CREATE EXTENSION {};'.format('hstore'))
            cur2.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
            conn.commit()
            conn.close()
            self.generate_license_and_migrate()
        except Exception, e:
            print (e)
            
    def format_machine(self, new_id):
        formatted = str(new_id)
        bb = base64.b64encode(bytes(formatted))
        bkey322 = bb.ljust(32)[:32]
        return bkey322

    def windows(self):
        machine_id = subprocess.check_output('wmic csproduct get UUID').split('\n')[1].strip()
        machine_model_number = subprocess.check_output('wmic csproduct get IdentifyingNumber').split('\n')[1].strip()
        new_id = '{0}@/{1}*'.format(machine_id, machine_model_number)
        mid = self.format_machine(new_id)
        return mid

    def generate_license(self):
        mac = self.windows()
        end_date = (datetime.today() + timedelta(days=30)).date().isoformat()
        gl = GetLicense(mac, end_date)
        return gl.license()

    def generate_license_and_migrate(self):
        try:
            keyfiles = self.generate_license()
            keyfile, check = keyfiles.split('###')
            keyfile = keyfile.replace('\r', '').replace('\n', '')
            check = check.replace('\r', '').replace('\n', '')

            subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','makemigrations'], shell=True)
            subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','migrate',], shell=True)
            # conn2 = psycopg2.connect("dbname='saleor' user='saleor' host='127.0.0.1' password='saleor'")
            # conn2.autocommit = True
            conn2 = self.connect_database()
            cur3 = conn2.cursor()
            cur3.execute("""INSERT INTO userprofile_user(name, email, is_superuser, is_active, is_staff, password, image, send_mail, date_joined) values('admin', 'admin@example.com', True, True, True, 'pbkdf2_sha256$30000$28uVy3qLTKlJ$npN/SiLkufzhREcOyYQFmWmzh1s/ZIo5qXk9/qSWSmE=','', True, now())""")
            cur3.execute("""INSERT INTO site_files(file, "check", created, modified) values('"""+keyfile+"""', '"""+check+"""', now(), now())""")
            conn2.commit()
            conn2.close()
        except Exception, e:
            print (e)
            