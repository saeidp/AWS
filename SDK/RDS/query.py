from helper import *
from sql_statement import *

# df = Query.query("select * from student_data_ods.student1.da_engagement_stage_current order by stu_id")
# S3.copy_to_s3_bucket("bucket", df):
#------------------------------------------------------------------

# accessing ODS database and run queries against it
# Jinja
jinja= Jinja()

try:
    Client.create_connection_from_secret_manager()
    # print("Creating table da_engagement_stage_current. If table exists then truncating it")
    # tableExist = Metadata.get_table('student1', 'da_engagement_stage_current')
    # if(not tableExist):
    #     Query.execute(create_staging_table)
    #     Query.execute(alter_staging_table)
    #     Query.execute(grant_select_on_staging_table_to_test_user)
    #     Query.execute(grant_select_on_staging_table_to_dataplatform_read)
    # else:
    #     Query.execute(truncate_staging_table)
    
    print("Getting student selection criteria values from s3 bucket")
    content = S3.get_student_selection_criteria("student-management-configuration-369025142683")
    print(content)

    print("Calling student1.set_param function to update parameters table")
    for key in content:
        Query.call_proc('student_data_ods.student1.set_param', [key,content[key]])

    print("truncating staging table")
    Query.execute(truncate_staging_table)
    
    print("Insering distinct id's into staging table")
    Query.execute(insert_staging_table_distinct_id)

    print('Updating staging table using materialized view')
    Query.execute(update_staging_table_set_some_fields)
    
    print('Updating staging table set start and end dates')
    Query.execute(update_staging_table_set_start_and_end_dates)

    print('Updating contact phone to yes in staging table')
    Query.execute(update_staging_table_contact_ph_yes)

    print('Updating contact phone to No for null values in staging table')
    Query.execute(update_staging_table_contact_ph_to_no_if_null)

    print('Updating first offer date in staging table')
    Query.execute(update_staging_table_set_first_offer_date)

    print('Updating offer acceptance date in staging table')
    Query.execute(update_staging_table_set_offer_acceptance_date)

    print('Updating first enrolment date in staging table')
    Query.execute(update_staging_table_set_first_enrolment_date)

    print('Updating tax file number in staging table')
    Query.execute(update_staging_table_set_tax_file_number)

    print('Updating tax file number to no if not found in staging table')
    Query.execute(update_staging_table_set_tax_file_number_to_no_if_is_null)

    print('Updating tax file cert fg (student has a CP sanction) in staging table')
    Query.execute(update_staging_table_set_tax_file_cert_fg)

    print('Updating tax file cert fg to no if tax file number is yes in staging table')
    Query.execute(update_staging_table_set_tax_file_cert_fg_to_no_if_tax_file_number_fg_is_yes)

    print('Updating tax file cert fg to no if it is null in staging table')
    Query.execute(update_staging_table_set_tax_file_cert_fg_to_no_if_is_null)

    print('Updating unique stu identifier to Yes in staging table')
    Query.execute(update_staging_table_set_unique_student_identifier_fg_to_yes)

    print('Updating unique stu identifier to No if it is null in staging table')
    Query.execute(update_staging_table_set_unique_student_identifier_fg_to_no_if_is_null)

    print('Updating step up bomus in staging table')
    Query.execute(update_staging_table_set_step_up_bonus)

    print('Updating step up bonus to No if it is null in staging table')
    Query.execute(update_staging_table_set_step_up_bonus_to_No_if_is_null)

    print('Updating first in family in staging table')
    Query.execute(update_staging_table_set_first_in_family)

    print('Updating first in family to No if it is null in staging table')
    Query.execute(update_staging_table_set_first_in_family_to_No_if_is_null)
    
    print('Updating sanctions with hold in staging table')
    Query.execute(update_staging_table_set_sanctions_with_hold)
    
    print('Updating sanctions with hold to No if it is null in staging table')
    Query.execute(update_staging_table_set_sanctions_with_hold_to_No_if_is_null)

    print('Updating progression agreement in staging table')
    Query.execute(update_staging_table_set_progression_agreement)

    print('Updating progression agreement to No if it is null in staging table')
    Query.execute(update_staging_table_set_progression_agreement_to_No_if_is_null)

    print('Updating post code in staging table')
    Query.execute(update_staging_table_set_post_code)

    print('Updating post code to NA if it is null in staging table')
    Query.execute(update_staging_table_set_post_code_to_NA_if_is_null)

    print('Updating low socio economic post code in staging table')
    Query.execute(update_staging_table_set_low_socio_economic_postcode)
    
    print('Updating low socio economic post code to NA if it is empty in staging table')
    Query.execute(update_staging_table_set_low_socio_economic_postcode_to_NA_if_is_empty)

    print('Updating student type in staging table')
    Query.execute(update_staging_table_set_student_type)

    print('Updating class registeration in staging table')
    Query.execute(update_staging_table_set_class_registeration)

    print('Updating class registeration to No if it is null in staging table')
    Query.execute(update_staging_table_set_class_registeration_to_No_if_is_null)
    
    print('Updating late enrolment in staging table')
    Query.execute(update_staging_table_set_late_enrolment)
    
    print('Updating late enrolment to No if it is null in staging table')
    Query.execute(update_staging_table_set_late_enrolment_to_No_if_is_null)

    print('Updating late offer provided in staging table')
    Query.execute(update_staging_table_set_late_offer_provided)
    
    print('Updating late offer provided to No if it is null in staging table')
    Query.execute(update_staging_table_set_late_offer_provided_to_No_if_is_null)

    print('Updating late offer acceptance in staging table')
    Query.execute(update_staging_table_set_late_offer_acceptance)

    print('Updating late offer acceptance to No if it is null in staging table')
    Query.execute(update_staging_table_set_late_offer_acceptance_to_No_if_is_null)

    print('Updating campus in staging table')
    Query.execute(update_staging_table_set_campus)

    print('Updating fee payment complete fg in staging table')
    Query.execute(update_staging_table_set_fee_payment_complete_fg)

    print('Updating sponsorship fg in staging table')
    Query.execute(update_staging_table_set_sponsorship_fg)

    print('Updating scholarship fg in staging table')
    Query.execute(update_staging_table_set_scholarship_fg)


    # Select data from da_engagement_stage_current
    df = Query.select(select_staging_table_ordered)
    # df['stu_id'] = df['stu_id'].apply(Student.pii_column_obfuscation)
    # df['indigenous_fg'] = df['indigenous_fg'].apply(Student.pii_column_obfuscation)
    S3.copy_to_landing_bucket('dp-main-landing-student-management-test', df.fillna(""))
    print(df)


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



# This is how you can use psycopg using parameters
#  cursor.itersize = 10000

#     sql = '''SELECT a.session_id, a.event_type, a.data, b.user_id,
#     a.timestamp
#     FROM public.activity_accumulator a
#     left join public.users b on a.user_pk1 = b.pk1
#     WHERE a.timestamp >= %(start_date)s and timestamp < %(end_date)s
#     ;'''

#     cursor.execute(sql,{"start_date":start_date,"end_date":end_date})

#     record = cursor.fetchall()

#     df = pd.DataFrame(record,columns=['session_id','event_type','data','user_id','timestamp'])



# delete locks
# CREATE OR REPLACE VIEW public.active_locks AS 
#  SELECT t.schemaname,
#     t.relname,
#     l.locktype,
#     l.page,
#     l.virtualtransaction,
#     l.pid,
#     l.mode,
#     l.granted
#    FROM pg_locks l
#    JOIN pg_stat_all_tables t ON l.relation = t.relid
#   WHERE t.schemaname <> 'pg_toast'::name AND t.schemaname <> 'pg_catalog'::name
#   ORDER BY t.schemaname, t.relname;
  
#   SELECT * FROM active_locks;
#   SELECT pg_cancel_backend(28997);
#   SELECT pg_terminate_backend(21962)