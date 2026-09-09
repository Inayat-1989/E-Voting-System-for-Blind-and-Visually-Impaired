document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("start-btn");
    const statusText = document.getElementById("voice-status");
    let mediaStream = null;

    const MAX_DURATION_MS = 10000;       // absolute safety cap
    const SILENCE_THRESHOLD = 10;        // volume level (0-255) below which we count as "quiet"
    const SILENCE_DURATION_MS = 1800;    // how long they must stay quiet before we stop

    if (!startBtn) {
        console.warn("Start button ('#start-btn') not found in login.html.");
        return;
    }

    function playBeep() {
        return new Promise((resolve) => {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.frequency.value = 800;
            gainNode.gain.value = 0.3;
            oscillator.start();
            setTimeout(() => {
                oscillator.stop();
                audioCtx.close();
                resolve();
            }, 300);
        });
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
            startBtn.disabled = false;
            if (statusText) statusText.textContent += " (Press Start to try again.)";
        }
    }

    async function recordAndSend() {
        try {
            if (!mediaStream) {
                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            }

            await playBeep();

            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioCtx.createMediaStreamSource(mediaStream);
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            const dataArray = new Uint8Array(analyser.frequencyBinCount);

            const mediaRecorder = new MediaRecorder(mediaStream);
            const audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) audioChunks.push(event.data);
            };

            let stopped = false;
            function finishRecording() {
                if (stopped) return;
                stopped = true;
                if (mediaRecorder.state !== "inactive") mediaRecorder.stop();
                audioCtx.close();
            }

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                await sendAudioToBackend(audioBlob);
            };

            if (statusText) statusText.textContent = "Sunte hain... Bolain.";
            mediaRecorder.start();

            const startTime = Date.now();
            let speechStarted = false;
            let silenceStart = null;

            function checkVolume() {
                if (stopped) return;

                analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
                const average = sum / dataArray.length;

                // Uncomment this line while tuning to see live volume numbers in console:
                console.log("volume:", average.toFixed(1));

                const now = Date.now();
                const elapsed = now - startTime;

                if (average > SILENCE_THRESHOLD) {
                    speechStarted = true;
                    silenceStart = null;
                } else if (speechStarted) {
                    if (silenceStart === null) silenceStart = now;
                    if (now - silenceStart > SILENCE_DURATION_MS) {
                        finishRecording();
                        return;
                    }
                }

                if (elapsed > MAX_DURATION_MS) {
                    finishRecording();
                    return;
                }

                requestAnimationFrame(checkVolume);
            }

            requestAnimationFrame(checkVolume);

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