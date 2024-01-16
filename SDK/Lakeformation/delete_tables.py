
import boto3
from botocore.exceptions import ClientError
import sys

client = boto3.client('glue')
def delete_a_table_from_database(database_name, table_name):
    try:
      response = client.delete_table(DatabaseName= database_name, Name = table_name)
      return response
    except ClientError as e:
      raise Exception( "boto3 client error in delete_a_table_from_database: " + e.__str__())
    except Exception as e:
      raise Exception("Unexpected error in delete_a_table_from_database: " + e.__str__())


delete_a_table_from_database('dp_main_blackboard_learn_db', 'blackboard_learn_blackboard_learn')