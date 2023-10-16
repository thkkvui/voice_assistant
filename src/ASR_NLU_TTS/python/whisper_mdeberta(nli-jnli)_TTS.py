import torch
import whisper
from transformers import pipeline, AutoTokenizer
import pyaudio
import wave
import re
import MeCab
import alkana
import pandas as pd
from TTS.api import TTS
import librosa
import sounddevice as sd

import asyncio
loop = asyncio.get_event_loop()
api_interval = 1800

intent_labels = ["天気", "ニュース", "予定", "マーケット"]
sample_outputs = {"天気":"今日は晴れ、予想最高気温は21℃です。",
           "ニュース":"オリンピック陸上100メートル決勝は雨天順延となりました。",
           "マーケット":"今日のドル円は150円です。",
           "予定":"12時から会議、17時から東京で会食、が予定されています。"
}

# Record
record_filepath = "record.wav"
sample_rate = 44100

# ASR
asr_model = whisper.load_model("base")

# NLU
model_name = "thkkvui/mDeBERTa-v3-base-finetuned-nli-jnli"

# TTS
tts_filepath = "output.wav"
tts_model = "tts_models/ja/kokoro/tacotron2-DDC"
# tts_model_en = "tts_models/en/ljspeech/tacotron2-DDC"
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

def intent_inference(asr_text):
    model_name = "thkkvui/mDeBERTa-v3-base-finetuned-nli-jnli"
    classifier = pipeline("zero-shot-classification", model=model_name)
    output = classifier(asr_text, intent_labels, multi_label=False)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    ids = tokenizer.encode(asr_text)
    tokens = tokenizer.convert_ids_to_tokens(ids, skip_special_tokens=True)
    return tokens, output["labels"][0]

def speech(answer_text):
    tts.tts_to_file(answer_text, file_path=tts_filepath, progress_bar=False, gpu=False)
    y, sr = librosa.load(tts_filepath, sr=sample_rate)
    sd.play(y, sr)
    sd.wait()
    return

async def get_queue(queue):
    while True:
        speechText = await queue.get()
        if speechText is None:
            break
        else:
            speech(speechText)

async def actions(tokens, intent):
    if "もし" in tokens:
        if intent=="天気":
            data_classified = ner_inference(tokens)
            term_list = get_terms(data_classified)
            scheduler.add_job(check_weather_conditions, "interval", minutes=api_interval/60)  # intervalを設定
            scheduler.start()
            await WeatherForecast2(term_list[0], term_list[1], term_list[2], term_list[3])
            await get_queue(speech_queue)
        elif intent=="ニュース":
            pass
        elif intent=="予定":
            pass
        elif intent=="マーケット":
            pass
    else:
        if intent=="天気":
            speech(sample_outputs[intent])
        elif intent=="ニュース":
            speech(sample_outputs[intent])
        elif intent=="予定":
            speech(sample_outputs[intent])
        elif intent=="マーケット":
            speech(sample_outputs[intent])
    return


async def main():
    # asr_sample1 = "今日の天気"
    # asr_sample2 = "もし今日11時の東京の天気が晴れになったら通知して"
    record()
    asr_text = data_preprocessing()
    tokens, intent = intent_inference(asr_text)
    await actions(tokens, intent)
    loop.stop()


if __name__ == "__main__":
    loop.run_until_complete(main())
    loop.run_forever()
    