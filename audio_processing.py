import soundfile as sf
import subprocess, json
from file_info import get_mime_type

def process_audio(file_name, file_id, download_path):
    try:
        command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", download_path]
        output = subprocess.check_output(command).decode()
        probe_data = json.loads(output)

        info = sf.info(download_path)

        mime_type = get_mime_type(download_path)

        return {
            "file_id": file_id,
            "mime_type": mime_type,
            "data": {
                "duration": int(probe_data['format']['duration']),
                "bit_rate": int(probe_data['format']['bit_rate']),
                "sample_rate": int(info['samplerate']),
                "channels": int(info['channels'])
            }
        }
    except Exception as e:
        print(f"Erro ao processar áudio {file_name}: {str(e)}")
        return None