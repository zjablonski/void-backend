import base64
import os
import uuid

import whisper
from pydub import AudioSegment
import base64
import io


def decode_base64_to_audio(base64_audio, format='mp4'):
    decoded_audio = base64.b64decode(base64_audio)
    audio_segment = AudioSegment.from_file(io.BytesIO(decoded_audio), format=format)
    return audio_segment


def transcribe_audio_from_base64(audio_list):
    combined_audio = sum([decode_base64_to_audio(audio) for audio in audio_list])
    filename = f"{str(uuid.uuid4())}.m4a"
    combined_audio.export(filename, format='mp4')
    model = whisper.load_model("large-v2")
    result = model.transcribe(filename, fp16=False)
    os.remove(filename)
    return result["text"]


if __name__ == "__main__":
    with open("test_data.txt", 'r', encoding='utf-8') as file:
        base64_audio1 = file.read()

    with open("test_data2.txt", 'r', encoding='utf-8') as file:
        base64_audio2 = file.read()
    print(transcribe_audio_from_base64([base64_audio1, base64_audio2]))

