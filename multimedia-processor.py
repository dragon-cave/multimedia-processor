import json
import pyffmpeg
import os
from .aws.s3.s3 import  client
from .aws.sqs.sqs import sqsclient
from PIL import Image
import io
from typeverification import get_file_type_by_mimetype
# Definir a URL da fila SQS
queue_url = os.getenv('QUEUE_URL')

def process_image(bucket, key):
    try:
        download_path = f'/tmp/{key}'
        client.download_file(bucket, key, download_path)
        
        
        with Image.open(download_path) as img:
            img.thumbnail((128, 128))
            
          
            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format=img.format)
            
           
            thumb_buffer.seek(0)
            
           
            thumb_key = f'image-thumbnails/{key}'
            
           
            client.upload_fileobj(thumb_buffer, bucket, thumb_key)
            
            print(f"Thumbnail criada e enviada para S3 como {thumb_key}")
        
       
        os.remove(download_path)

    except Exception as e:
        print(f"Erro ao processar imagem {key}: {str(e)}")

#def process_audio(bucket, key):
    try:
        
        pass
    except Exception as e:
        print(f"Erro ao processar áudio {key}: {str(e)}")
def process_file(bucket, key, file_type):
    if file_type == 'video':
        process_video(bucket, key)
    elif file_type == 'image':
        process_image(bucket, key)
    else:
        print(f"Unsupported file type: {file_type}")

def process_video(bucket, key):
    try:
       
        local_video_path = f'/tmp/{key}'
        client.download_file(bucket, key, local_video_path)
        
      
        thumbnail_path = f'/tmp/thumbnail_{key}.jpg'
        video = pyffmpeg.FFMPEG(local_video_path)
        video.options('-vf', 'thumbnail,scale=320:240').save(thumbnail_path)
        
        
        thumbnail_key = f'video-thumbnails/{key}.jpg'
        client.upload_file(thumbnail_path, bucket, thumbnail_key)
        
      
        resolutions = {
            '1080p': '1920:1080',
            '720p': '1280:720',
            '480p': '854:480'
        }
        
        for label, resolution in resolutions.items():
            output_path = f'/tmp/{label}_{key}'
            video.options('-vf', f'scale={resolution}').save(output_path)
            output_key = f'{label}/{key}'
            client.upload_file(output_path, bucket, output_key)
        
        
        os.remove(local_video_path)
        os.remove(thumbnail_path)
        for label in resolutions.keys():
            os.remove(f'/tmp/{label}_{key}')

    except Exception as e:
        print(f"Erro ao processar vídeo {key}: {str(e)}")

def main():
    while True:
        try:
            
            response = sqsclient.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10 
            )
            
            messages = response.get('Messages', [])
            
            if not messages:
                print("Nenhuma mensagem recebida. Aguardando novas tarefas...")
                continue
            
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    bucket = body['bucket']
                    key = body['key']
                    
                    file_type = get_file_type_by_mimetype(key)
                    print(f"Processing {file_type} from bucket {bucket} with key {key}")
                    process_file(bucket, key, file_type)
                    
                except Exception as e:
                    print(f"Erro ao processar a mensagem {message['MessageId']}: {str(e)}")
                
                finally:
                    sqsclient.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    
        except Exception as e:
            print(f"Erro ao receber mensagens do SQS: {str(e)}")

if __name__ == "__main__":
    main()
