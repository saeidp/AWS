import boto3
import logging
logger = logging.getLogger()
glue_client = boto3.client('glue', region_name='ap-southeast-2') 

def get_existing_glue_tables(glue_client, db_name):
    ''' Fetch the list of the table names in the database '''
    next_token = ""
    existing_tables_list = []
    while True:
        existing_tables = glue_client.get_tables(DatabaseName= db_name, NextToken=next_token)
        for table in existing_tables.get('TableList'):
            existing_tables_list.append(table.get('Name'))
        next_token = existing_tables.get('NextToken')
        if next_token is None:
            break
    return existing_tables_list

tables = get_existing_glue_tables(glue_client, 'dp_main_blackboard_learn_db')
print(tables)