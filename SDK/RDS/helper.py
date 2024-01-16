import pandas as pd
import psycopg2
import json
import os
import io
import boto3
import botocore
from copy import deepcopy
from six import string_types
from jinjasql import JinjaSql
from datetime import datetime
import hashlib
from datetime import datetime
from dateutil import tz



class Client:
    activeConnection = None
    # Create a global psql connection object
    def __init__(self, user, password, database, host):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        global connection
        connection = psycopg2.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
        )
        Client.activeConnection = connection

    def __repr__(self):
        return "User {0} connected to {1}.".format(self.user, self.database)

    @classmethod
    # Easy login with json
    def from_json(cls, file_path):
        with open(file_path, mode="r") as json_file:
            # Store credentials to the global namespace
            global credentials
            credentials = json.load(json_file)
        # Use credentials to log in
        return cls(
            credentials["user"],
            credentials["password"],
            credentials["database"],
            credentials["host"],
        )

    @classmethod
    def create_connection_from_secret_manager(cls):
        global credentials
        region_name = "ap-southeast-2"
        secret_name = "stuDataOds-dataplatform"
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        credentials = json.loads(
            client.get_secret_value(SecretId=secret_name)["SecretString"]
        )
        return cls(
            credentials["username"],
            credentials["password"],
            credentials["dbname"],
            "studataodsinstance1.cqr2uygkhlnz.ap-southeast-2.rds.amazonaws.com",
        )


class Query:
    @classmethod
    # Retrieve column names in given table
    def get_columns(cls, table):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT * FROM {0} LIMIT 0    
        """.format(
                table
            )
        )
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        return colnames

    @classmethod
    # Return subset of table
    def fetch(cls, table, num_records):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT * FROM {0} LIMIT {1}    
        """.format(
                table, num_records
            )
        )
        result = cursor.fetchall()
        cursor.close()
        columns = Query.get_columns(table)
        df = pd.DataFrame(result, columns=columns)
        return df

    @classmethod
    # Get all records
    def fetchall(cls, table):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT * FROM {0}
        """.format(
                table
            )
        )
        result = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        df = pd.DataFrame(result, columns=colnames)
        return df

    @classmethod
    # Basic query
    def select(cls, query):
        cursor = connection.cursor()
        cursor.execute(
            """
        {0}
        """.format(
                query
            )
        )
        result = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        df = pd.DataFrame(result, columns=colnames)
        return df

    @classmethod
    def execute(cls, query):
        cursor = connection.cursor()
        cursor.execute(
            """
        {0}
        """.format(
                query
            )
        )
        connection.commit()
        result = cursor.rowcount
        cursor.close()
        return result

    @classmethod
    def call_proc(cls, proc, params):
        cursor = connection.cursor()
        cursor.callproc(proc, params)
        connection.commit()
        result = cursor.fetchall()
        cursor.close
        return result



class Metadata:
    @classmethod
    # See all tables in DB instance
    def get_tables(cls, schema):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = '{0}' """.format(
                schema
            )
        )
        result = cursor.fetchall()
        cursor.close()
        if len(result) < 1:
            result = "There are no tables in this database"
        return result

    @classmethod
    # See all tables in DB instance
    def get_tables(cls, schema):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = '{0}' """.format(
                schema
            )
        )
        result = cursor.fetchall()
        cursor.close()
        if len(result) < 1:
            result = "There are no tables in this database"
        return result

    @classmethod
    # See all tables in DB instance
    def get_table(cls, schema, table):
        cursor = connection.cursor()
        cursor.execute(
            """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = '{0}' and table_name = '{1}' """.format(
                schema, table
            )
        )
        result = cursor.fetchall()
        cursor.close()
        if len(result) < 1:
            return False
        return True

class Student:
    @classmethod
    def pii_column_obfuscation(cls, value):
        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


class S3:
    def utc_to_local(utc_date_str):
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Australia/Perth')
        utc = datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        return datetime.strftime(central, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def copy_to_landing_bucket(cls, bucket_name, df):
        df['ts_insert'] = df['ts_insert'].apply(cls.utc_to_local)

        df['year'] = df['ts_insert'].apply(lambda x: str(x)[:4])
        df['month'] = df['ts_insert'].apply(lambda x: str(x)[5:7])
        df['day'] = df['ts_insert'].apply(lambda x: str(x)[8:10])

        ts_date = df['ts_insert'].apply(lambda x: str(x)[:10]).iat[0]
        
        file_name = f"student-management_{ts_date}.json"
        year = ts_date[:4]
        month = ts_date[5:7]
        day = ts_date[8:10]
        key_path = f"student-management/{year}/{month}/{day}/{file_name}"
        json_buffer = io.StringIO()
        df.to_json(json_buffer,orient ="records")
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(Key=key_path, Body=json_buffer.getvalue(),ServerSideEncryption='AES256')

    @classmethod
    def get_student_selection_criteria(cls, bucket_name):
        object_key = "student-selection_criteria.json"
        s3 = boto3.resource("s3")

        try:
            s3.Object(bucket_name, object_key).load()
        except botocore.exceptions.ClientError as e:
            print(f"{object_key} does not exist in bucket {bucket_name}")
            student_selection_criteria_object = {
                "location_cd": "1",
                "avail_yr": "2023",
                "sprd_cd": "1"
            }
            
            print("creating student selection criteria file")
            json_content = json.dumps(student_selection_criteria_object)
            bucket = s3.Bucket(bucket_name)
            bucket.put_object(Key=object_key, Body=json_content)
            return json.loads(json_content)

        content_object = s3.Object(bucket_name, object_key)
        file_content = content_object.get()["Body"].read().decode("utf-8")
        return json.loads(file_content)




class Jinja:
    def quote_sql_string(self, value):
        """
        If `value` is a string type, escapes single quotes in the string
        and returns the string enclosed in single quotes.
        """
        if isinstance(value, string_types):
            new_value = str(value)
            new_value = new_value.replace("'", "''")
            return "'{}'".format(new_value)
        return value

    def get_sql_from_template(self, query, bind_params):
        if not bind_params:
            return query
        params = deepcopy(bind_params)
        for key, val in params.items():
            params[key] = self.quote_sql_string(val)
        return query % params

    def apply_sql_template(self, template, parameters):
        """
        Apply a JinjaSql template (string) substituting parameters (dict) and return
        the final SQL.
        """
        j = JinjaSql(param_style="pyformat")
        query, bind_params = j.prepare_query(template, parameters)
        return self.get_sql_from_template(query, bind_params)















        # for key, items in df.groupby('ts_date'):
        #     file_name = "student-management_" + str(key[:10]) + ".json"
        #     year = key[:4]
        #     month = key[5:7]
        #     day = key[8:10]
        #     key_path = f"student-management/{year}/{month}/{day}/{file_name}"
        #     json_buffer = io.StringIO()
        #     df[df["ts_date"] == key].to_json(json_buffer,orient ="records")
        #     s3 = boto3.resource('s3')
        #     bucket = s3.Bucket(bucket_name)
        #     bucket.put_object(Key=key_path, Body=json_buffer.getvalue(),ServerSideEncryption='AES256')
