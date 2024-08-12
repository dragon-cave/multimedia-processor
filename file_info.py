import os, magic

def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type

def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension.lower() 