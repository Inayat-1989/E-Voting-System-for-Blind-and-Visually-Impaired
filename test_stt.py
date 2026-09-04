from faster_whisper import WhisperModel

print("Loading model... (first time takes a minute, downloads ~500MB)")
model = WhisperModel("small", device="cpu", compute_type="int8")

segments, info = model.transcribe("test_audio2.m4a", language="ur")

print("Detected language:", info.language)
full_text = ""
for segment in segments:
    full_text += segment.text

print("TRANSCRIPT:", full_text)