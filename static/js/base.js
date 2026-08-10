// ---------- TTS: makes the system speak ----------
function speak(text, onDone) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    if (onDone) utterance.onend = onDone;
    window.speechSynthesis.speak(utterance);
}

// ---------- Contrast theme ----------
const savedTheme = localStorage.getItem('contrast-theme');
if (savedTheme === 'high-contrast') {
    document.documentElement.setAttribute('data-theme', 'high-contrast');
}

const toggleBtn = document.getElementById('contrast-toggle');

function updateButtonText(theme) {
    if (theme === 'high-contrast') {
        toggleBtn.innerText = "Switch to Normal Contrast";
    } else {
        toggleBtn.innerText = "Switch to High Contrast";
    }
}

updateButtonText(localStorage.getItem('contrast-theme'));

toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'high-contrast') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('contrast-theme', 'normal');
        updateButtonText('normal');
    } else {
        document.documentElement.setAttribute('data-theme', 'high-contrast');
        localStorage.setItem('contrast-theme', 'high-contrast');
        updateButtonText('high-contrast');
    }
});

// ---------- Speech elements ----------
const startBtn = document.getElementById('start-btn');
const statusSpan = document.getElementById('status');
const transcriptSpan = document.getElementById('transcript');
const serverResponseSpan = document.getElementById('server-response');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    statusSpan.innerText = "Web Speech API not supported in this browser.";
    startBtn.disabled = true;
} else {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    let step = 'ask_signin';
    let silentTries = 0;
    const MAX_SILENT_TRIES = 3;
    let cnicTries = 0;                     // NEW: counts failed CNIC verifications
    const MAX_CNIC_TRIES = 3;              // NEW: limit before giving up
    let pendingCnic = '';
    let started = false;

    function listen() {
        statusSpan.innerText = "Listening...";
        recognition.start();
    }

    function askSignIn() {
        step = 'ask_signin';
        speak("Welcome to the e-voting system. Do you want to sign in with your I D? Say yes, okay, or no.", listen);
    }

    function askCnic() {
        step = 'ask_cnic';
        speak("Please say your C N I C number now.", listen);
    }

    function askConfirmCnic() {
        step = 'confirm_cnic';
        speak("You said " + pendingCnic.split('').join(' ') +
              ". Is that your C N I C number? Say yes or no.", listen);
    }

    recognition.onresult = (event) => {
        console.log("RAW HEARD:", event.results[0][0].transcript, "| step:", step);
        const heard = event.results[0][0].transcript.toLowerCase().trim();
        transcriptSpan.innerText = heard;
        statusSpan.innerText = "Heard you.";
        silentTries = 0;

        if (step === 'ask_signin') {
            const saidYes = heard.includes('yes') || heard.includes('okay') ||
                            heard.includes('ok') || heard.includes('i want');
            if (saidYes) {
                askCnic();
            } else {
                askSignIn();
            }
        }
        else if (step === 'ask_cnic') {
            const digits = heard.replace(/\D/g, '').slice(0, 13);
            if (digits.length === 13) {
                pendingCnic = digits;
                askConfirmCnic();
            } else {
                speak("I heard only " + digits.length + " digits. Let's try again.", askCnic);
            }
        }
        else if (step === 'confirm_cnic') {
            const saidYes = heard.includes('yes') || heard.includes('okay') ||
                            heard.includes('ok') || heard.includes("it's okay") || heard.includes('it is');
            if (saidYes) {
                statusSpan.innerText = "Checking with server...";
                sendToDjango(pendingCnic);
            } else {
                speak("Okay, let's try again.", askCnic);
            }
        }
    };

    recognition.onerror = (event) => {
        console.log("ERROR TYPE:", event.error, "| step:", step);
        statusSpan.innerText = "Error occurred: " + event.error;

        if (event.error === 'not-allowed') {
            speak("Microphone access is blocked. Please allow the microphone and press any key.");
            started = false;
            return;
        }

        silentTries = silentTries + 1;

        if (silentTries >= MAX_SILENT_TRIES) {
            speak("I did not hear a response. When you are ready, press any key to start again.");
            started = false;
            silentTries = 0;
            step = 'ask_signin';
            statusSpan.innerText = "Waiting. Press any key to start again.";
        } else {
            if (step === 'ask_signin') askSignIn();
            else if (step === 'ask_cnic') askCnic();
            else if (step === 'confirm_cnic') askConfirmCnic();
        }
    };

    recognition.onend = () => {
        if (statusSpan.innerText === "Listening...") {
            statusSpan.innerText = "Stopped listening.";
        }
    };

    // ---------- Starting the conversation ----------
    function startDialog() {
        if (started) return;
        started = true;
        askSignIn();
    }
    window.addEventListener('keydown', startDialog);
    window.addEventListener('click', startDialog);

    startBtn.addEventListener('click', () => {
        started = true;
        askSignIn();
    });

    // ---------- Backend call ----------
    function sendToDjango(text) {
        fetch('/api/process-speech/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            serverResponseSpan.innerText = data.message;
            if (data.verified) {
                cnicTries = 0;                                     // NEW: reset on success
                statusSpan.innerText = "Verified!";
                speak("You are a verified disabled user. Welcome!", function () {
                    const cnicField = document.getElementById('cnic');
                    if (cnicField) {
                        cnicField.value = pendingCnic;
                        cnicField.closest('form').submit();
                    }
                });
            } else {
                statusSpan.innerText = "Not found.";
                cnicTries = cnicTries + 1;                         // NEW: count the failure

                if (cnicTries >= MAX_CNIC_TRIES) {                 // NEW: give up at three
                    speak("No voter found after three attempts. Please contact the polling staff for help. Press any key to start again.");
                    started = false;
                    cnicTries = 0;
                    step = 'ask_signin';
                    statusSpan.innerText = "Waiting. Press any key to start again.";
                } else {
                    speak("No voter found with that C N I C. Attempt " + cnicTries + " of three. Let's try again.", askCnic);
                }
            }
        })
        .catch(error => {
            statusSpan.innerText = "Server Error";
            console.error('Error:', error);
            speak("Sorry, there was a server problem. Let's try again.", askCnic);
        });
    }
}