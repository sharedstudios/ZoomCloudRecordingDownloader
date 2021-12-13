import boto3
from boto.s3.connection import S3Connection
import sys
from boto.s3.key import Key
import os

# Get all transcribing results from S3, AWS access key id and secret access key are under api.txt

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3 = session.resource('s3')

bucket_name = 'transcribe-audio-result-bucket'
bucket = s3.Bucket(bucket_name)
count = 0
for obj in bucket.objects.all():
    count += 1
    obj_name = obj.key
    destination = "./AWS_Transcript_Results/" + obj_name.replace('*', '+').replace('!', '=') # ! and = are illegal for s3 object name
    bucket.download_file(obj_name,destination)

print(count)


