import json
import pyffmpeg
import os
from .aws.client import  aws_manager,bucket_name
from PIL import Image
import soundfile as  sf
import pyffmpeg
import mimetypes
import io
from typeverification import get_file_type_by_mimetype
from aws.sqs.dequeue import dequeue_json_object
from aws.s3.s3 import download_file
# Definir a URL da fila SQS
queue_url = os.getenv('QUEUE_URL')
s3client=aws_manager.get_s3_client()
sqsclient=aws_manager.get_sqs_client()

def main():
    while True:
        try:
            payload = dequeue_json_object()

            file_name = payload['file_name']
            user_id = payload['user_id']
            file_id = payload['file_id']

            file_path = f'users/{user_id}/files/{file_name}'
            local_file_path = f'/tmp/{file_name}'
            
            download_file(file_path, local_file_path)

            mime_type = get_mime_type(local_file_path)

            request_data = None

            if mime_type.startswith('image/'):
                request_data = process_image(user_id, file_name, file_id)
            elif mime_type.startswith('video/'):
                request_data = process_video(user_id, file_name, file_id)
            elif mime_type.startswith('audio/'):
                request_data = process_audio(user_id, file_name, file_id)

            os.remove(local_file_path)

            # Send request to the webhook endpoint!
                    
        except Exception as e:
            print(f"Erro ao receber mensagens do SQS: {str(e)}")

if __name__ == "__main__":
    main()
