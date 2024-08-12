import soundfile as sf
import subprocess
import json

def process_audio(file_name, file_id, download_path, mime_type):
    try:
        # Use ffprobe to get detailed information about the audio file
        command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", download_path]
        output = subprocess.check_output(command).decode()
        probe_data = json.loads(output)

        # Get audio file info using soundfile
        info = sf.info(download_path)

        # Extract necessary details from the probe data and soundfile info
        duration = float(probe_data['format']['duration'])
        bit_rate = int(probe_data['format']['bit_rate'])
        sample_rate = int(info.samplerate)
        channels = int(info.channels)

        # Return the processed audio details
        return {
            "file_id": file_id,
            "mime_type": mime_type,
            "data": {
                "duration": duration,
                "bit_rate": bit_rate,
                "sample_rate": sample_rate,
                "channels": channels
            }
        }
    except Exception as e:
        print(f"Erro ao processar áudio {file_name}: {str(e)}")
        return None
