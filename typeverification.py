import mimetypes

def get_file_type_by_mimetype(key):
    mime_type, _ = mimetypes.guess_type(key)

    if mime_type:
        if mime_type.startswith('image'):
            return 'image'
        elif mime_type.startswith('video'):
            return 'video'
    return 'unknown'


