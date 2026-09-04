from gtts import gTTS

text = "Aap ki tasdeeq ho gayi hai. Welcome."

tts = gTTS(text=text, lang="ur")
tts.save("test_output.mp3")

print("Done! Check test_output.mp3 in this folder.")