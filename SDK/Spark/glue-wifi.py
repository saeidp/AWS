# the fixed version of wifi glue job
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
import json
import re

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME',
                                    'input_path',
                                    'input_bucket',
                                    'output_path',
                                    'output_bucket',
                                    'input_format',
                                    'input_type',
                                    'output_partition_keys'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
# Create Logger
logger = glueContext.get_logger()
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

input_path = args['input_path']         # 'wifi/cmx-messages-job-test/'
input_bucket = args['input_bucket']     # 'curtin-dmf-examples-dev'
output_path = args['output_path']       # 'wifi/cmx_preprocessed-job-test/'
output_bucket = args['output_bucket']   # 'curtin-dmf-examples-dev'
input_format = args['input_format']     # 'json' 'csv'
input_type = args['input_type']         # 'cmx-association'
partition_keys = json.loads(args['output_partition_keys']) # "['floors','something']"



full_input_path = 's3://{}/{}'.format(
                    input_bucket,
                    input_path)
full_output_path = 's3://{}/{}'.format(
                    output_bucket,
                    output_path)

## @type: DataSource
## @args: 
## @return: DataSource0
## @inputs: []


if input_format == 'json':
    format_options = {"multiline": True}
elif input_format == 'csv':
    format_options = {"withHeader": True}

DataSource0 = glueContext.create_dynamic_frame_from_options(
    connection_type = "s3",
    connection_options={'paths': [full_input_path], 'recurse': True},
    format=input_format,
    format_options=format_options,
    transformation_ctx = "{}-Source".format(input_type))
    
DataSource0.printSchema()

DataSourceChoicesResolved = DataSource0.resolveChoice(choice = "cast:string", transformation_ctx = "{}-ResolveChoice".format(input_type))

DataSourceChoicesResolved_temp_DF = DataSourceChoicesResolved.toDF()
columns = DataSourceChoicesResolved_temp_DF.columns
if ("eventId" in columns and "floorId" in columns and "confidenceFactor" in columns):
    DataSourceChoicesResolved_DF= DataSourceChoicesResolved_temp_DF \
        .withColumn("eventId", DataSourceChoicesResolved_temp_DF["eventId"].cast("String")) \
        .withColumn("floorId", DataSourceChoicesResolved_temp_DF["floorId"].cast("String"))  \
        .withColumn("confidenceFactor", DataSourceChoicesResolved_temp_DF["confidenceFactor"].cast("String"))
else:
    DataSourceChoicesResolved_DF = DataSourceChoicesResolved_temp_DF

DataSourceChoicesResolved_DF.printSchema()

for c in DataSourceChoicesResolved_DF.columns:
        # Replace: period, ampersand, backslash, forwardslash, colon, whitespace, hyphen, left and right round bracket with underscore.
        DataSourceChoicesResolved_DF = DataSourceChoicesResolved_DF.withColumnRenamed(c , re.sub(r"[.&\\\/:\s,\-\(\)]","_", c))


DataSourceRenamedColumns = DynamicFrame.fromDF(DataSourceChoicesResolved_DF, glueContext, 'dyf_renamed_columns')

## @type: DataSink
## @args: [connection_type = "s3", format = "glueparquet", connection_options = {"path": "s3://dp-main-curation-dev/dts/wifi/cmx/association/", "compression": "snappy", "partitionKeys": ["floor"]}, transformation_ctx = "DataSink0"]
## @return: DataSink0
## @inputs: [frame = DataSource0]
DataSink0 = glueContext.write_dynamic_frame.from_options(
    frame = DataSourceRenamedColumns,
    connection_type = "s3",
    format = "glueparquet",
    connection_options = {"path": full_output_path, "partitionKeys": partition_keys}, transformation_ctx = "{}-sink".format(input_type))

job.commit()