import os
from os.path import join

import pandas as pd
from gtts import gTTS

from root.settings import BASE_DIR


def generate_audio_world(en_world):
    # os.makedirs(join(BASE_DIR , 'media/vocab/audio'), exist_ok=True)

    try:
        tts = gTTS(text=en_world, lang='en')
        audio_file_path = os.path.join(BASE_DIR , "media/vocab/audio", f"{en_world}.mp3")
        tts.save(audio_file_path)
        print(f"Audio generated: {audio_file_path}")
        return audio_file_path
    except Exception as e:
        print(f"Error generating audio for 'book': {e}")


def generate_audio_from_excel(excel_path):
    # ?os.makedirs(BASE_DIR , output_folder, exist_ok=True)
    df = pd.read_excel(excel_path)
    if 'eng' not in df.columns:
        raise KeyError("The Excel file must contain a column named 'eng' for English words.")
    for index, row in df.iterrows():
        english_word = row['eng']
        if pd.isna(english_word):
            continue
        try:
            tts = gTTS(text=english_word, lang='en')
            audio_file_path = os.path.join(BASE_DIR, "media/vocab/audio"  f"{english_word}.mp3")
            tts.save(audio_file_path)
            print(f"Audio generated: {audio_file_path}")
        except Exception as e:
            print(f"Error generating audio for '{english_word}': {e}")
