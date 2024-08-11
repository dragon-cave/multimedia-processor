import io
import exifread
from aws.s3.s3 import upload_file
from PIL import Image

def process_image(user_id, file_name, file_id, download_path, mime_type):
    try:
        with Image.open(download_path) as img:
            width, height = img.size
            color_depth = len(img.getbands()) * 8

            # Generate thumbnail
            thumb_height = 256
            thumb_width = int((thumb_height / height) * width)
            img.thumbnail((thumb_width, thumb_height))

            # Save thumbnail to buffer
            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format=img.format)
            thumb_buffer.seek(0)

            # Upload thumbnail to S3
            thumb_key = f'users/{user_id}/files/{file_name}/thumbnail.png'
            upload_file(thumb_buffer, thumb_key)

            # Extract EXIF data
            exif_data = {}
            with open(download_path, 'rb') as img_file:
                tags = exifread.process_file(img_file)
                for tag, value in tags.items():
                    # Convert EXIF data to string for JSON serialization
                    exif_data[tag] = str(value)

            return {
                "file_id": file_id,
                "mime_type": mime_type,
                "data": {
                    "width": int(width),
                    "height": int(height),
                    "color_depth": int(color_depth),
                    "resolution": f"{int(width)}x{int(height)}",
                    "exif_data": exif_data
                },
            }
    except Exception as e:
        print(f"Error processing image {file_name}: {str(e)}")
        return None
