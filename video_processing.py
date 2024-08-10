import pyffmpeg, os
from aws.s3.s3 import upload_file
from file_info import get_file_extension, get_mime_type

def process_video(user_id, file_name, file_id, download_path):
    try:
        local_thumbnail_path = f'/tmp/{file_name}.png'
        video = pyffmpeg.FFMPEG(download_path)
        info = video.info()
        video.options('-vf', 'thumbnail,scale=320:240').save(local_thumbnail_path)

        # Read the file as BytesIO
        with open(local_thumbnail_path, 'rb') as f:
            thumbnail_path = f'users/{user_id}/files/{file_name}/thumbnail.png'
            upload_file(f, thumbnail_path)
        
        os.remove(local_thumbnail_path)
      
        resolutions = {
            '1080p': '1080',
            '720p': '720',
            '480p': '480'
        }
        
        for label, resolution in resolutions.items():
            extension = get_file_extension(download_path)
            local_output_path = f'/tmp/{label}.{extension}'
            video.options('-vf', f'scale=-1:{resolution}').save(local_output_path)
            # output_key = f'{label}/{file_name}'
            
            with open(local_output_path, 'rb') as f:
                output_path = f'users/{user_id}/files/{file_name}/processed/{label}.{extension}'
                upload_file(f, output_path)

            os.remove(local_output_path)
        
        duration = info['duration']
        resolution = info['resolution']
        frame_rate = info['frame_rate']
        video_codec = info['video_codec']
        audio_codec = info['audio_codec']
        bit_rate = info['bit_rate']

        mime_type = get_mime_type(download_path)

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
        