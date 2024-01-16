import boto3
from botocore.exceptions import ClientError
import sys

client = boto3.client('glue')


def get_glue_tables(database=None):
   
    next_token = ""
    tables = []
    count = 0

    while True:
        response = client.get_tables(
            DatabaseName=database,
            NextToken=next_token
        )

        for table in response.get('TableList'):
            print(table.get('Name'))
            tables.append(table.get("Name"))
            count +=1

        next_token = response.get('NextToken')

        if next_token is None:
            print(count)
            break
    return tables

# select tables
tables=[]
tables = get_glue_tables('dp_main_wifi_cmx_db')
sys.stdout = open('output.txt', 'wt')
for table in tables:
    print(table)
sys.stdout.close()


#  responseGetDatabases = client.get_databases()

# databaseList = responseGetDatabases['DatabaseList']

# for databaseDict in databaseList:
#     databaseName = databaseDict['Name']
#     if(databaseName == 'dp_student_one'):
#         print('\ndatabaseName: ' + databaseName)

#         responseGetTables = client.get_tables( DatabaseName = databaseName )
#         tableList = responseGetTables['TableList']

#         for tableDict in tableList:
#             tableName = tableDict['Name']
#             print('\n-- tableName: '+tableName)    