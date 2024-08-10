import json
import os
from aws.client import aws_manager
# Define the SQS queue URL
queue_url = os.getenv('QUEUE_URL')
sqsclient=aws_manager.get_sqs_client
def enqueue_video_processing(s3_bucket, s3_key):
    message_body = {
        'bucket': s3_bucket,
        'key': s3_key
    }
    
    response = sqsclient.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
    
    print(f"Enqueued video processing task with Message ID: {response['MessageId']}")

