import csv

from json import load
import csvvalidator

import boto3


class VerifyFileSchemaException(Exception):
    pass

s3 = boto3.resource('s3')

def _load_object_content(bucket, key):
    '''
    load_object_content Loads the given object (identified by
    bucket and key) from S3

    :param bucket:  The S3 bucket name
    :type bucket: Python String
    :param key: The S3 object key
    :type key: Python String
    :return: Contents of S3 object as a string
    :rtype: Python String
    '''
    s3_object = s3.Object(bucket, key)
    return s3_object.get()["Body"].read().decode('utf-8')

def _verify_csv_schema(file_content, separator, schema):
    '''
    _verify_csv_schema Verifies the schema of csv data. Only required
    column names are confirmed

    :param file_content: The content of the file
    :type file_content: Python String
    :param separator: The delimeter character used in the file
    :type separator: Python Character
    :param schema: The csv schema we are expecting
    :type schema: Python String
    :raises Exception: When file_content schema is incorrect
    '''
    file_content_lines = file_content.splitlines()
    csv_reader = csv.reader(file_content_lines, delimiter=separator)

    field_names = []
    schema_properties = schema['properties']
    for prop in schema_properties:
        field_names.append(prop['field'])

    # field_names = tuple(schema['properties'])

    validator = csvvalidator.CSVValidator(tuple(field_names))
    validator.add_header_check('EX1', 'bad header')

    for prop in schema_properties:
        prop_field = prop['field']
        prop_type = prop['type']
        if prop_type == 'int':
            validator.add_value_check(prop_field, int, 'EX_INT', prop_field + ' must be an integer')
        elif prop_type == 'string':
            validator.add_value_check(prop_field, str, 'EX_STR', prop_field + ' must be a string')
        elif prop_type == 'enum':
            enum_values = tuple(prop['values'])
            validator.add_value_check(prop_field, csvvalidator.enumeration(enum_values), 'EX_ENUM', prop_field + ' must have value from enum')

    problems = validator.validate(csv_reader)

    if len(problems) > 0:
        raise VerifyFileSchemaException(str(problems))
key = "marketing-automation/2023/06/01/Marketo_Lead_01062023021235.csv"
bucket= "dp-main-landing-marketing-automation-dev"

file_content = _load_object_content(bucket, key)
separator = ','
with open("c:/dev/GitHub/AWS/SDK/SchemaValidation/CSV/schema.json") as f:
    jsonFile = load(f)
schema = jsonFile["schema"]
_verify_csv_schema(file_content, separator, schema)