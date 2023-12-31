import torch
import whisper
from transformers import pipeline
import pyaudio
import wave
import re
import MeCab
import alkana
import pandas as pd
from TTS.api import TTS
import librosa
import sounddevice as sd

sample_outputs = {"weather_query":"今日は晴れ、予想最高気温は21℃です。",
           "news_query":"オリンピック陸上100メートル決勝は雨天順延となりました。",
           "qa_currency":"今日のドル円は150円です。",
           "calendar_query":"12時から会議、17時から東京で会食、が予定されています。"
}

# Record
record_filepath = "record.wav"
sample_rate = 44100

# ASR
asr_model = whisper.load_model("base")

# NLU
model_name = "thkkvui/xlm-roberta-base-finetuned-massive"

# TTS
tts_filepath = "output.wav"
tts_model = "tts_models/ja/kokoro/tacotron2-DDC"
tts = TTS(tts_model)


def record():
    record_time = 8
    FORMAT = pyaudio.paInt16        
    rate = sample_rate
    chunk = 2**10
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        input=True,
                        rate=rate, 
                        frames_per_buffer=chunk,
                        channels=1,
    )

    print(f"Speak to your microphone for {record_time} sec...")
    frames = []
    for i in range(0, int(rate / chunk * record_time)):
        data = stream.read(chunk)
        frames.append(data) 
    print ("Great!")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    wf = wave.open(record_filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return

def data_preprocessing():
    asr_text = asr_model.transcribe(record_filepath, verbose=False, language="ja")

    al_re = re.compile(r'^[a-zA-Z]+$')
    def is_al(text):
        return al_re.match(text) is not None
    
    tmp_text = asr_text["text"]
    wakati = MeCab.Tagger('-Owakati')
    wakati_output = wakati.parse(tmp_text)
    
    # 英語検索
    df = pd.DataFrame(wakati_output.split(" "),columns=["word"])
    df["en_word"] = df["word"].apply(is_al)
    df["katakana"] = df["word"].apply(alkana.get_kana)
    # カタカナ変換
    df = df[df["en_word"] == True]
    dict_rep = dict(zip(df["word"], df["katakana"]))
    
    if len(df) > 0:
        for word, katakana in dict_rep.items():
            asr_text = tmp_text.replace(word, katakana)
    else:
        asr_text = tmp_text

    print(asr_text)
    return asr_text

def inference(asr_text):
    model_name = "thkkvui/xlm-roberta-base-finetuned-massive"
    classifier = pipeline("text-classification", model=model_name)
    output = classifier(asr_text)
    answer_text = sample_outputs[output[0]["label"]]
    return answer_text

def speech(answer_text):
    tts.tts_to_file(answer_text, file_path=tts_filepath, progress_bar=False, gpu=False)
    y, sr = librosa.load(tts_filepath, sr=sample_rate)
    sd.play(y, sr)
    sd.wait()
    return

def main():
    record()
    asr_text = data_preprocessing()
    answer_text = inference(asr_text)
    speech(answer_text)


if __name__ == "__main__":
    main()
    