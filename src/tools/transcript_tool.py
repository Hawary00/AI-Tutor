import whisper

def transcript_loader(audio_path):
    """Transcribes a local audio/video file using OpenAI Whisper."""
    model = whisper.load_model("tiny")

    try:
        result = model.transcribe(audio_path)
        transcription = result["text"]
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

    return transcription