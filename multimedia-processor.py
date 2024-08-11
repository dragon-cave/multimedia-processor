from dotenv import load_dotenv
load_dotenv()

import os, requests
from aws.sqs.dequeue import dequeue_json_object
from aws.s3.s3 import download_file
from file_info import get_mime_type
from audio_processing import process_audio
from image_processing import process_image
from video_processing import process_video

def main():
    backend_url = os.getenv('BACKEND_URL')
    while True:
        try:
            payload = dequeue_json_object()

            if payload is None:
                continue

            file_name = payload['file_name']
            user_id = payload['user_id']
            file_id = payload['file_id']

            file_path = f'users/{user_id}/files/{file_name}'
            local_file_path = f'/tmp/{file_name}'
            
            download_file(file_path, local_file_path)

            mime_type = get_mime_type(local_file_path)

            request_data = None

            if mime_type.startswith('image/'):
                request_data = process_image(user_id, file_name, file_id, local_file_path)
            elif mime_type.startswith('video/'):
                request_data = process_video(user_id, file_name, file_id, local_file_path)
            elif mime_type.startswith('audio/'):
                request_data = process_audio(file_name, file_id, local_file_path)

            os.remove(local_file_path)

            url = f'{backend_url}/api/webhook/'
            requests.post(url, json=request_data, verify=False)
        except Exception as e:
            print(f"Erro ao receber mensagens do SQS: {str(e)}")

if __name__ == "__main__":
    main()
