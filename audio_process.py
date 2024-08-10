from aws.s3.s3 import download_file
import mimetypes
import soundfile as  sf
import os
from .aws.client import  aws_manager,bucket_name
s3client=aws_manager.get_s3_client()

def process_audio(user_id,file_name,file_id):
    try:
        download_path = f'/tmp/{file_name}'
        s3client.download_file(bucket_name, file_name, download_path)

        info = mediainfo(download_path)
        duration = float(info['duration'])
        bit_rate = int(info['bit_rate'])
        sample_rate = int(info['sample_rate'])
        channels = int(info['channels'])

        mime_type = get_mime_type(download_path)

        os.remove(download_path)

        return {
            "file_id": file_id,
            "mime_type": mime_type,
            "data": {
                "duration": duration,
                "bit_rate": bit_rate,
                "sample_rate": sample_rate,
                "channels": channels
            }
        }

    except Exception as e:
        print(f"Erro ao processar áudio {file_name}: {str(e)}")
        return None