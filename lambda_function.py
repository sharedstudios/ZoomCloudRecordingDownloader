import boto3
import uuid
import json
import re
from urllib.parse import unquote


def lambda_handler(event, context):
    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']

    print(s3bucket)
    print(s3object)

    s3Path = "s3://" + s3bucket + "/" + s3object
    s3Path = unquote(s3Path)
    outputKeyName = unquote(s3object).replace("-audio_transcript", "").replace(".mp3", ".json").replace("+",
                                                                                                        "*").replace(
        "=", "!")
    jobName = s3object + '-' + str(uuid.uuid4())
    print(jobName)
    jobName = re.sub('[^A-Za-z0-9]+', '', jobName)

    client = boto3.client('transcribe')

    response = client.start_transcription_job(
        TranscriptionJobName=jobName,
        LanguageCode='en-US',
        MediaFormat='mp3',
        Media={
            'MediaFileUri': s3Path
        },
        OutputBucketName="transcribe-audio-result-bucket",
        OutputKey=outputKeyName
    )

    return {
        'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
    }
