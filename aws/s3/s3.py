from aws.client import bucket_name, aws_manager
import io

def list_files(prefix=''):
    response = aws_manager.get_s3_client().list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return response.get('Contents', [])

def generate_presigned_url(file_name, expiration=3600):
    return aws_manager.get_s3_client().generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': file_name},
        ExpiresIn=expiration
    )

def delete_file(file_name):
    aws_manager.get_s3_client().delete_object(Bucket=bucket_name, Key=file_name)

def upload_file(file, file_name):
    aws_manager.get_s3_client().upload_fileobj(file, bucket_name, file_name)

def download_file(file_name, output_path):
    aws_manager.get_s3_client().download_file(bucket_name, file_name, output_path)

def get_file_object(file_name):
    s3_client = aws_manager.get_s3_client()
    file_object = io.BytesIO()
    s3_client.download_fileobj(bucket_name, file_name, file_object)
    file_object.seek(0)  # Move the cursor to the beginning of the file object
    return file_object
