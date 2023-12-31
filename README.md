## **音声アシスタントの構築**

〜初めての方へ〜
- [このプロジェクトについて（thkkvui.blog）](https://thkkvui.blog/2023/04/19/post7/)
- [コンセプト](https://github.com/thkkvui/Deploy_my_VUI)

&emsp;

## **サンプルコード**

　実装と動作テストに使用したコードの抜粋です。ASR, TTSはOSSの学習済みモデルを使用しています。

### 1. **Question Answering** 
　QAタスク用の自然言語モデルを使用したコードです。

 - [whisper_roberta(JaQuAD)_TTS.ipynb](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/nb/whisper_roberta(JaQuAD)_TTS.ipynb)

 - [whisper_roberta(JaQuAD)_TTS.py](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/python/whisper_roberta(JaQuAD)_TTS.py)

### 2. **Classification**
　分類タスク用の自然言語モデル（Text Classification、Zero-Shot Classification）を使用したコードです。

#### [Text Classification]
 - [whisper_roberta(massive)_TTS.ipynb](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/nb/whisper_roberta(massive)_TTS.ipynb)
 - [whisper_roberta(massive)_TTS.py](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/python/whisper_roberta(massive)_TTS.py)

#### [Zero-Shot Classification]
 - [whisper_mDeBERTa(nli-jnli)_TTS.ipynb](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/nb/whisper_mdeberta(nli-jnli)_TTS.ipynb)
 - [whisper_mDeBERTa(nli-jnli)_TTS.py](https://github.com/thkkvui/voice_assistant/blob/main/src/ASR_NLU_TTS/python/whisper_mdeberta(nli-jnli)_TTS.py)

### 3. **LLM**
 - [whisper-gpt2(wikipedia)_TTS.ipynb]()

&emsp;

## **ブログ**

　それぞれの音声アシスタントについて説明したブログになります。

### 1. Question Answering 
 - [音声アシスタントを作る 〜試作品の動作テスト〜](https://thkkvui.blog/2023/07/30/post26/)
 - [音声アシスタントを作る 〜試作品を仕上げる（失敗）〜](https://thkkvui.blog/2023/09/14/post29/)

### 2. Classification
 - [音声アシスタントを作る 〜試作品を仕上げる〜](https://thkkvui.blog/2023/10/06/post37/)

### 3. LLM 
