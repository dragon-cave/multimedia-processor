import io
from aws.client import  aws_manager,bucket_name
from aws.s3.s3 import upload_file
from PIL import Image

def process_image(user_id, file_name, file_id, download_path):
    try:
        with Image.open(download_path) as img:
            width, height = img.size
            color_depth = len(img.getbands()) * 8
            exif_data = img._getexif() if img._getexif() else {}
            
            thumb_height = 256
            thumb_width = int((thumb_height / height) * width)
            img.thumbnail((thumb_width, thumb_height))

            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format=img.format)
            
            thumb_buffer.seek(0)
           
            thumb_key = f'user/{user_id}/files/{file_name}/thumbnail.png'
            
            upload_file(thumb_buffer, thumb_key)

            color_depth = len(img.getbands()) * 8

            exif_data = img._getexif()

            return {
                "file_id": file_id,
                "mime_type": "image/png",
                "data": {
                    "width": width,
                    "height": height,
                    "color_depth": color_depth,
                    "resolution": f"{width}x{height}",
                    "exif": exif_data
                },
            }
    except Exception as e:
           print(f"Erro ao processar imagem {file_name}: {str(e)}")