## **音声アシスタントの構築**

〜初めての方へ〜
- [このプロジェクトについて（thkkvui.blog）](https://thkkvui.blog/2023/04/19/post7/)
- [コンセプト](https://github.com/thkkvui/Deploy_my_VUI)

&emsp;

## **1. プロトタイプ**

　このプロジェクトはAmazon AlexaやGoogle Assistantの使用を前提としていません。Built-in且つタスク処理型の音声アシスタントは、ユーザー学習やプログラムなどをカスタムメイドする点で不向きであると判断しました。そのため最初は音声アシスタントのプロトタイプ作成からスタートし、そこから追加機能を実装する流れで順次作業を進めていきます。

　ASR, NLU, TTSについては、主にOSSの学習済みモデルを使用します。できる限りサイズが小さく且つ性能の良い音声アシスタントを構築したいので、中身は随時変更していくことになると思います。

### ASR
 - [whisper(openai)](https://github.com/openai/whisper)

### NLU
 - [xlm-roberta-base(Hugging Face)](https://huggingface.co/xlm-roberta-base)

### TTS
 - [voicevox(VOICEVOX)](https://github.com/VOICEVOX/voicevox)
 - [TTS(coqui-ai)](https://github.com/coqui-ai/TTS)

### HD

&emsp;