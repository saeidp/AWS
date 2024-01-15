import boto3

glue_client = boto3.client("glue", "us-west-2")

def delete_partitions(database, table, partitions, batch=25):
    for i in range(0, len(partitions), batch):
      to_delete = [{k:v[k]} for k,v in zip(["Values"]*batch, partitions[i:i+batch])]
      glue_client.batch_delete_partition(
        DatabaseName=database,
        TableName=table,
        PartitionsToDelete=to_delete)

def get_and_delete_partitions(database, table):
    paginator = glue_client.get_paginator('get_partitions')
    itr = paginator.paginate(DatabaseName=database, TableName=table)
    
    for page in itr:
      delete_partitions(database, table, page["Partitions"])