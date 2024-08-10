from aws.s3.s3 import download_file
import os
from .aws.client import  aws_manager,bucket_name
import io
from PIL import Image


s3client=aws_manager.get_s3_client()
def process_image(user_id, file_name,file_id):
    try:
        download_path = f'/tmp/{file_name}'
        s3client.download_file(bucket_name, file_name, download_path)
        
        
        with Image.open(download_path) as img:
            img.thumbnail((128, 128))
            width, height = img.size
            color_depth = len(img.getbands()) * 8
            exif_data = img._getexif() if img._getexif() else {}
            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format=img.format)
            
           
            thumb_buffer.seek(0)
            
           
            thumb_key = f'user/{user_id}/files/{file_name}'
            
           
            s3client.upload_fileobj(thumb_buffer, bucket_name, thumb_key)

            color_depth = len(img.getbands()) * 8

            exif_data = img._getexif()
            # Filtrar informações importantes do EXIF (se disponível)

        os.remove(download_path)
        print(f"Thumbnail criada e enviada para S3 como {thumb_key}")
        
       
        

    except Exception as e:
           print(f"Erro ao processar imagem {file_name}: {str(e)}")

    return {
            "file_id": file_id,
            "mime_type": "image/jpeg",
            "data": {
                "width": width,
                "height": height,
                "color_depth": color_depth,
                "resolution": f"{width}x{height}",
                "exif_data": exif_data
            }
        }
            
