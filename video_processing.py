import os
import subprocess
import json
from aws.s3.s3 import upload_file

def get_video_info(file_path):
    try:
        # Run ffprobe command to get video information
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]

        output = subprocess.check_output(command).decode()
        probe = json.loads(output)

        # Extract video stream info
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

        # Convert frame_rate from ratio to float
        frame_rate_str = video_stream.get('avg_frame_rate', '0/1')
        numerator, denominator = map(int, frame_rate_str.split('/'))
        frame_rate = numerator / denominator

        # Extract information
        info = {
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "format": probe['format']['format_name'],
            "duration": float(video_stream['duration']),  # Duration as float
            "resolution": f"{video_stream.get('width', 'unknown')}x{video_stream.get('height', 'unknown')}",
            "frame_rate": frame_rate,  # Frame rate as float
            "video_codec": video_stream.get('codec_name', 'unknown'),
            "audio_codec": audio_stream.get('codec_name', 'unknown') if audio_stream else 'unknown',
            "bit_rate": int(probe['format'].get('bit_rate', '0'))
        }

        return info

    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {str(e)}")
        return None

def process_video(user_id, file_name, file_id, download_path):
    try:
        # Extract video information
        info = get_video_info(download_path)
        if info is None:
            raise ValueError("Failed to get video information.")

        # Generate thumbnail
        local_thumbnail_path = f'/tmp/{file_name}.jpg'
        command = [
            'ffmpeg', '-ss', '00:00:01.00',  # Seek to 1 second
            '-i', download_path,
            '-vf', 'scale=320:320:force_original_aspect_ratio=decrease',  # Scale with aspect ratio
            '-vframes', '1',  # Extract a single frame
            local_thumbnail_path
        ]
        subprocess.run(command, check=True)

        # Upload thumbnail
        with open(local_thumbnail_path, 'rb') as f:
            thumbnail_path = f'users/{user_id}/files/{file_name}/thumbnail.jpg'
            upload_file(f, thumbnail_path)

        os.remove(local_thumbnail_path)

        # Process video for different resolutions
        resolutions = {
            '1080p': '1080',
            '720p': '720',
            '480p': '480'
        }

        for label, resolution in resolutions.items():
            local_output_path = f'/tmp/{label}.mp4'
            command = [
                'ffmpeg', '-i', download_path,
                '-vf', f'scale=-2:{resolution}',  # Ensure width is divisible by 2
                '-c:v', 'libx264',  # Use libx264 codec for video
                '-c:a', 'aac',  # Use AAC codec for audio
                local_output_path
            ]
            subprocess.run(command, check=True)
            
            # Upload processed video
            with open(local_output_path, 'rb') as f:
                output_path = f'users/{user_id}/files/{file_name}/processed/{label}.mp4'
                upload_file(f, output_path)

            os.remove(local_output_path)

        return {
            "file_id": file_id,
            "mime_type": "video/mp4",  # Adjust as needed
            "data": info
        }

    except Exception as e:
        print(f"Error processing video {file_name}: {str(e)}")
        return None
