import json
import jsonlines
import numpy as np
import os
import boto3

Bucket = 'pipe-line-test-2'

# Prefix = 'ss-demo'
# Answere = 'yes'
# JobRef = "RovPipeLabelingJob-ref"
# JobRefMetadata = "'RovPipeLabelingJob-ref-metadata"
# HumanAnnotated = "human-annotated"

# Prefix = 'ss-demo-human-yes'
# Answere = 'yes'
# JobRef = "RovPipeLabelingJob-ref"
# JobRefMetadata = "'RovPipeLabelingJob-ref-metadata"
# HumanAnnotated = "human-annotated"

# Prefix = 'ss-demo-human-no'
# Answere = 'no'
# JobRef = "RovPipeLabelingJob-ref"
# JobRefMetadata = "'RovPipeLabelingJob-ref-metadata"
# HumanAnnotated = "human-annotated"

# Prefix = 'ss-demo-human-verified'
# Answere = 'no'
# JobRef = "Verify-MachineLabelled-Dataset2-ref"
# JobRefMetadata = "RovPipeLabelingJob-ref-metadata"
# HumanAnnotated = "human-annotated"

Prefix = 'ss-demo-kmeans'
JobRef = "Human-pipe-segmentation-Kmeans-ref"
JobRefMetadata = "Human-pipe-segmentation-Kmeans-ref-metadata"
HumanAnnotated = "human-annotated"
Answere = 'yes'

with jsonlines.open('output.manifest', 'r') as reader:
    lines = list(reader)
    # Shuffle data in place.
np.random.shuffle(lines)

if(Answere != 'both'):
    if (Answere == 'no'):
        lines = [line for line in lines if (
            line.get(JobRef) != None and line[JobRefMetadata][HumanAnnotated] == "no")]
    if (Answere == 'yes'):
        lines = [line for line in lines if (
            line.get(JobRef) != None and line[JobRefMetadata][HumanAnnotated] == "yes")]
else:
    lines = [line for line in lines if (
        line.get(JobRef) != None)]


dataset_size = len(lines)
num_training_samples = round(dataset_size*0.8)

train_data = lines[:num_training_samples]
validation_data = lines[num_training_samples:]
print(len(train_data))
print(len(validation_data))

s3 = boto3.resource('s3')
train_path = '{}/train/'.format(Prefix)
train_annotation_path = '{}/train_annotation/'.format(Prefix)
count = 0
print("Start process for copying train images")
for data in train_data:
    img_url = data['source-ref']
    img_url = img_url.split("//")[1]
    img_file = os.path.basename(img_url)
    s3.Object(Bucket, train_path +
              img_file).copy_from(CopySource=img_url)

    seg_url = data[JobRef]
    seg_url = seg_url.split("//")[1]
    seg_file = img_file.split(".")[0] + '.png'
    s3.Object(Bucket, train_annotation_path +
              seg_file).copy_from(CopySource=seg_url)
    count += 1
print("Total Train images: {}".format(count))
validation_path = '{}/validation/'.format(Prefix)
validation_annotation_path = '{}/validation_annotation/'.format(Prefix)

count = 0
print("Start process for copying validation images")
for data in validation_data:
    img_url = data['source-ref']
    img_url = img_url.split("//")[1]
    img_file = os.path.basename(img_url)
    s3.Object(Bucket, validation_path +
              img_file).copy_from(CopySource=img_url)

    seg_url = data[JobRef]
    seg_url = seg_url.split("//")[1]
    seg_file = img_file.split(".")[0] + '.png'
    s3.Object(Bucket, validation_annotation_path +
              seg_file).copy_from(CopySource=seg_url)
    count += 1
print("Total validation images: {}".format(count))

# -----------------------------------------------

# if(Answere == 'no'):
#     newLines = []
#     for line in lines:
#         source = line.get("source-ref")
#         words = source.split("/")
#         if(line.get('RovPipeLabelingJob-ref') != None and words[3] == "dataset" and line['RovPipeLabelingJob-ref-metadata']['human-annotated'] == "no"):
#             newLines.append(line)
#     lines = newLines


# s33 = boto3.client('s3')
# result = s33.get_bucket_acl(Bucket=Bucket)
# print(result)


# I found another solution

# s3 = boto3.resource('s3')
# s3.Object('my_bucket','new_file_key').copy_from(CopySource='my_bucket/old_file_key')
# s3.Object('my_bucket','old_file_key').delete()

#    os.path.splitext(img_file)[0] + '.png'

# import boto3
# s3 = boto3.resource('s3')
# copy_source = {
#       'Bucket': 'mybucket',
#       'Key': 'mykey'
#     }
# bucket = s3.Bucket('otherbucket')
# bucket.copy(copy_source, 'otherkey')


# import boto3

# s3_resource = boto3.resource('s3')

# new_bucket_name = "targetBucketName"
# bucket_to_copy = "sourceBucketName"

# for key in s3.list_objects(Bucket=bucket_to_copy)['Contents']:
#     files = key['Key']
#     copy_source = {'Bucket': "bucket_to_copy",'Key': files}
#     s3_resource.meta.client.copy(copy_source, new_bucket_name, files)
#     print(files)

#  c= boto.connect_s3()
# src = c.get_bucket('my_source_bucket')
# dst = c.get_bucket('my_destination_bucket')

# for k in src.list():
#     # copy stuff to your destination here
#     dst.copy_key(k.key.name, src.name, k.key.name)
#     # then delete the source key
#     k.delete()


# img_file = os.path.basename(img_url)
# file_exists = os.path.exists(img_url)
