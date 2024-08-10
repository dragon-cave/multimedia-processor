import json
from aws.client import aws_manager, queue_url

def dequeue_json_object():
    """
    Dequeue a JSON object from the SQS queue.

    :return: The JSON object retrieved from the SQS queue, or None if no messages are available.
    """
    try:
        # Receive a message from the queue
        response = aws_manager.get_sqs_client().receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,  # Retrieve one message
            WaitTimeSeconds=10  # Long polling to reduce empty responses
        )
        
        messages = response.get('Messages', [])
        
        if messages:
            # Retrieve the first message
            message = messages[0]
            message_body = message['Body']
            
            # Convert the JSON string back to a dictionary
            json_object = json.loads(message_body)
            
            # Delete the message from the queue after processing
            receipt_handle = message['ReceiptHandle']
            aws_manager.get_sqs_client().delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            
            return json_object
        else:
            print("No messages available.")
            return None
            
    except Exception as e:
        print(f"Failed to dequeue JSON object: {str(e)}")
        raise