from aws.s3.s3 import download_file
import pyffmpeg
from aws.client import  aws_manager, bucket_name
import os
from getfileinfo import 
def process_video(user_id, file_name,file_id):
    try:
       
        download_path = f'/tmp/{file_name}'
        aws_manager.get_s3_client().download_file(bucket_name, file_name, download_path)
        
      
        thumbnail_path = f'users/{user_id}/files/{file_name}'
        video = pyffmpeg.FFMPEG(download_path)
        info = video.info()
        video.options('-vf', 'thumbnail,scale=320:240').save(thumbnail_path)
        
        
        thumbnail_key = f'video-thumbnails/{file_name}.png'
        aws_manager.get_s3_client().upload_file(thumbnail_path, bucket_name, thumbnail_key)
        
      
        resolutions = {
            '1080p': '1920:1080',
            '720p': '1280:720',
            '480p': '854:480'
        }
        
        for label, resolution in resolutions.items():
            extension=get_file_extension(download_path)
            output_path = f'user/{user_id}/{label}.{extension}'
            video.options('-vf', f'scale={resolution}').save(output_path)
            output_key = f'{label}/{file_name}'
            aws_manager.get_s3_client().upload_file(output_path, bucket_name, output_key)
        
         
        # Extrair informações do vídeo
        os.remove(download_path)
        os.remove(thumbnail_path)
        for label in resolutions.keys():
            os.remove(f'/tmp/{label}_{file_name}')

        duration = info['duration']
        resolution = info['resolution']
        frame_rate = info['frame_rate']
        video_codec = info['video_codec']
        audio_codec = info['audio_codec']
        bit_rate = info['bit_rate']

        mime_type = get_mime_type(download_path)

        os.remove(download_path)

        return {
            "file_id": file_id,
            "mime_type": mime_type,
            "data": {
                "duration": duration,
                "resolution": resolution,
                "frame_rate": frame_rate,
                "video_codec": video_codec,
                "audio_codec": audio_codec,
                "bit_rate": bit_rate
            }
        }

    except Exception as e:
        print(f"Erro ao processar vídeo {file_name}: {str(e)}")
        