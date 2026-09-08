document.addEventListener("DOMContentLoaded", () => {
    const recordBtn = document.getElementById("record-btn");
    const statusText = document.getElementById("voice-status");
    const cnicField = document.getElementById("cnic");
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // Check if optional localStorage CNIC exists for fallback/testing
    if (cnicField) {
        const storedCnic = localStorage.getItem("CNIC");
        if (storedCnic) {
            cnicField.value = storedCnic;
            localStorage.removeItem("CNIC");
        }
    }

    if (!recordBtn) {
        console.warn("Record button element ('#record-btn') not found in login.html.");
        return;
    }

    // Toggle recording on button click
    recordBtn.addEventListener("click", async () => {
        if (!isRecording) {
            await startRecording();
        } else {
            stopRecording();
        }
    });

    // Hold Spacebar to Record for Accessibility
    document.addEventListener("keydown", async (e) => {
        if (e.code === "Space" && !isRecording && document.activeElement.tagName !== "INPUT") {
            e.preventDefault();
            await startRecording();
        }
    });

    document.addEventListener("keyup", (e) => {
        if (e.code === "Space" && isRecording && document.activeElement.tagName !== "INPUT") {
            e.preventDefault();
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                await sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            isRecording = true;
            if (statusText) statusText.textContent = "Sunte hain... Bolain (Recording...)";
            recordBtn.classList.add("recording-active");
        } catch (err) {
            console.error("Microphone access error:", err);
            if (statusText) statusText.textContent = "Microphone access denied or unsupported.";
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            if (statusText) statusText.textContent = "Processing speech...";
            recordBtn.classList.remove("recording-active");
        }
    }

    async function sendAudioToBackend(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "voter_speech.webm");

        try {
            const response = await fetch("/api/process-speech/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            // 1. Fill visual CNIC field if extracted by Gemini Flash
            if (data.cnic && cnicField) {
                cnicField.value = data.cnic;
                cnicField.dispatchEvent(new Event("input", { bubbles: true }));
            }

            // 2. Play ElevenLabs Urdu Audio Response
            if (data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play();

                // 3. Redirect to election page after confirmation audio finishes playing
                if (data.status === "success" && data.redirect_url) {
                    audio.onended = () => {
                        window.location.href = data.redirect_url;
                    };
                }
            } else if (data.status === "success" && data.redirect_url) {
                // Direct fallback redirect if audio URL is not present
                window.location.href = data.redirect_url;
            }

            if (statusText) {
                statusText.textContent = data.message || "Response received.";
            }

        } catch (error) {
            console.error("Error processing speech:", error);
            if (statusText) statusText.textContent = "Server error processing voice.";
        }
    }
});