document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("start-btn");
    const statusText = document.getElementById("voice-status");
    let mediaStream = null;
    const RECORD_DURATION_MS = 5000;

    if (!startBtn) {
        console.warn("Start button ('#start-btn') not found in login.html.");
        return;
    }

    startBtn.addEventListener("click", async () => {
        startBtn.disabled = true;
        try {
            const response = await fetch("/api/start-voice-login/");
            const data = await response.json();
            handleServerResponse(data);
        } catch (err) {
            console.error("Error starting voice login:", err);
            if (statusText) statusText.textContent = "Server error. Please try again.";
            startBtn.disabled = false;
        }
    });

    function handleServerResponse(data) {
        if (statusText) statusText.textContent = data.message || "";

        if (!data.audio_url) {
            afterAudioFinished(data);
            return;
        }

        const audio = new Audio(data.audio_url);
        audio.onended = () => afterAudioFinished(data);
        audio.play();
    }

    function afterAudioFinished(data) {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
            return;
        }

        if (data.continue_listening) {
            recordAndSend();
        } else {
            // Stopped (e.g. max attempts reached) - let voter press Start again
            startBtn.disabled = false;
            if (statusText) statusText.textContent += " (Press Start to try again.)";
        }
    }

    async function recordAndSend() {
        try {
            if (!mediaStream) {
                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            }
            const mediaRecorder = new MediaRecorder(mediaStream);
            const audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                await sendAudioToBackend(audioBlob);
            };

            if (statusText) statusText.textContent = "Sunte hain... Bolain.";
            mediaRecorder.start();

            setTimeout(() => {
                if (mediaRecorder.state !== "inactive") mediaRecorder.stop();
            }, RECORD_DURATION_MS);

        } catch (err) {
            console.error("Microphone error:", err);
            if (statusText) statusText.textContent = "Microphone access denied or unsupported.";
            startBtn.disabled = false;
        }
    }

    async function sendAudioToBackend(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "voter_speech.webm");

        try {
            if (statusText) statusText.textContent = "Processing...";
            const response = await fetch("/api/process-speech/", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            handleServerResponse(data);
        } catch (error) {
            console.error("Error processing speech:", error);
            if (statusText) statusText.textContent = "Server error processing voice.";
            startBtn.disabled = false;
        }
    }
});