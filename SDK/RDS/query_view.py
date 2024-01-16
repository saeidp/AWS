from helper import *
from sql_statement import *


jinja= Jinja()

try:
    Client.create_connection_from_secret_manager()

    print("Creating table da_parameters and insert initial parameters values")
    tableExist = Metadata.get_table('student1', 'da_parameters')
    if(not tableExist):
        Query.execute(create_parameters_table)
        Query.execute(insert_into_parameters_table)

    print("Create get param function")
    Query.execute(create_get_param_function)

    print("Create set param function")
    Query.execute(create_set_param_function)

    print("Create student mv default function")
    Query.execute(create_student_mv_default_function)

    
    print("Creating da_student_vw view")
    viewExist = Metadata.get_table('student1', 'da_student_vw')
    if(not viewExist):
        Query.execute(create_student_view)

    print("Create create_student_mv function")
    Query.execute(create_student_material_view_function)

    print("Getting student selection criteria values from s3 bucket")
    content = S3.get_student_selection_criteria("student-management-configuration-369025142683")
    print(content)

    print("Calling create_student_mv function to create materialized view")
    # Query.call_proc('student_data_ods.student1.create_student_mv', [content['avail_yr'],content['sprd_cd']])

except (Exception, psycopg2.Error) as error:
    print("Error while processing student data", error)
finally:
    if Client.activeConnection:
        Client.activeConnection.close()
        print("PostgreSQL connection is closed")






# s3 = boto3.resource('s3')
# bucket_name = os.environ['bucket_name']
# my_bucket = s3.Bucket(bucket_name)
# my_bucket.put_object(Key=key_path, Body=json_buffer.getvalue(),ServerSideEncryption='AES256')



# connection = psycopg2.connect(
#     user = "dataplatform",
#     password = "S_3ZH0PQiCEfg5wvQg0-PTlbodh=,T",
#     database = "student_data_ods",
#     host = "studataodsinstance1.cqr2uygkhlnz.ap-southeast-2.rds.amazonaws.com")
# print(connection)



# path = os.path.join(os.getcwd(), 'rds', 'aws_psql.json')
# client = Client.from_json(path)
# print(client)



# print(client)
# result = Metadata.get_tables('student1')
# print(result)
# df = Query.fetchall('student1.da_student_mv')
# print(df)
# df = Query.fetch('student1.da_student_mv', 10)
# print(df)


#  psycopg2-binary, pandas, and sqlalchemy must be installed.
# rds environment
# import boto3
# client = boto3.client('rds')
# response = client.describe_db_instances(DBInstanceIdentifier='studataodsinstance1')
# print(response)
#----------------------------------------------------
# params = {
#     'stu_id': 13676216
# }
# user_transaction_template = '''select * from student_data_ods.student1.da_engagement_stage_current where stu_id = {{ stu_id }}'''
# statement = jinja.apply_sql_template(user_transaction_template, params)
# print(statement)