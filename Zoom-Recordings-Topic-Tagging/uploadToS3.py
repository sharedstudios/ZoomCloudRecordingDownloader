import boto
import boto.s3
import sys
from boto.s3.key import Key
import os


bucket_name = 'transcribe-audio-result-bucket'
conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY)

bucket = conn.create_bucket(bucket_name,
    location=boto.s3.connection.Location.DEFAULT)

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if '.M4A' not in f:
        continue
    print ('Uploading %s to Amazon S3 bucket %s' % \
       (f, bucket_name))

    def percent_cb(complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()


    k = Key(bucket)
    k.key = f
    k.set_contents_from_filename(f,
        cb=percent_cb, num_cb=10)